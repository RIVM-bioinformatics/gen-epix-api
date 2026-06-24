"""
Benchmark comparing six distance-calculation variants for LSP-3477.

Six flag combinations (blob vs row-per-pair, Python vs numpy, scalar numpy vs
batched numpy) are timed on DICT and SA_SQLITE repositories at two scales.
Each variant runs on a FRESH copy of the repository so results are comparable.

Large SQLite base files are stored in BENCHMARK_DATA_DIR (D: drive). A
per-variant temp file is created by copying the base, populated with n_new
fresh profiles, used for the timed run, then deleted.

Run with:
    pytest test/seqdb/performance/calculate_seq_distances/ \\
        -k test_seqdb_distance_optimization_benchmark \\
        -m performance -v -s

For MSSQL, set SEQDB_MSSQL_TEST_URL and add -m "performance and mssql".
"""

import base64
import json
import logging
import os
import shutil
from pathlib import Path
from time import perf_counter
from typing import Any, cast
from uuid import UUID

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False

import numpy as np
import pyinstrument
import pytest
from pyinstrument.renderers import JSONRenderer

from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model
from test.seqdb.performance.calculate_seq_distances.base import (
    DEV_REPOSITORY_CONFIG,
    TEST_TYPE,
    VERBOSE,
)
from test.seqdb.performance.calculate_seq_distances.generate_seqdb_models import (
    generate_scale_test_db,
)
from test.seqdb.performance.common import (
    count_seq_profiles,
    create_dict_repository,
    create_mssql_repository,
    create_sqlite_repository,
    fill_empty_sqlite_repository,
    set_service_repository,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env

# ── Data storage ────────────────────────────────────────────────────────────
# Large SQLite base files live here so the repo tree stays clean.
BENCHMARK_DATA_DIR = Path("/mnt/d/data/rivm/lsp-3477-benchmark")

# ── Benchmark parameters ────────────────────────────────────────────────────
MSSQL_URL_ENV = "SEQDB_MSSQL_TEST_URL"

# existing_chunk_size for _calculate_and_store_distances (match prod default)
EXISTING_CHUNK_SIZE = 1000

# max_distance used for the retrieve sub-benchmark; set high so results are
# returned across all variants (avoids no-op queries skewing the timing).
RETRIEVE_MAX_DISTANCE = 1e9

N_EXISTING = [100, 1000, 5000]
N_NEW = [10, 50, 100]
N_LOCI = 3000

VARIANTS = [
    {"name": "blob_baseline",    "pair": False, "numpy": False, "batch": False},
    {"name": "blob_numpy",       "pair": False, "numpy": True,  "batch": False},
    {"name": "blob_numpy_batch", "pair": False, "numpy": True,  "batch": True},
    {"name": "pair_baseline",    "pair": True,  "numpy": False, "batch": False},
    {"name": "pair_numpy",       "pair": True,  "numpy": True,  "batch": False},
    {"name": "pair_numpy_batch", "pair": True,  "numpy": True,  "batch": True},
]
REPO_TYPES = [enum.RepositoryType.DICT, enum.RepositoryType.SA_SQLITE]

_RESULTS: list[dict[str, Any]] = []

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
)

# ── Module-level env fixture ─────────────────────────────────────────────────


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=SEQDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=False,
    )


# ── Profile generation helpers ───────────────────────────────────────────────


def _generate_new_profiles(
    n_new: int,
    allele_protocol_id: UUID,
    locus_set_id: UUID,
    n_loci: int,
    seed: int = 999,
) -> tuple[list[model.SeqProfile], list[model.Sample]]:
    """Generate n_new SeqProfile + Sample pairs with random allele IDs.

    No SeqDistance record is created; the caller inserts these directly into a
    fresh repo before running the timed distance-calculation step.
    """
    import random as _rnd

    rng = _rnd.Random(seed)

    def _uuid() -> UUID:
        return UUID(int=rng.getrandbits(128))

    profiles: list[model.SeqProfile] = []
    samples: list[model.Sample] = []
    for _ in range(n_new):
        allele_ids = [_uuid() for _ in range(n_loci)]
        sample = model.Sample(
            id=_uuid(),
            created_in_data_collection_id=_uuid(),
        )
        profile = model.SeqProfile(  # type: ignore[call-arg]
            id=_uuid(),
            seq_profile_type=enum.SeqProfileType.ALLELE,
            protocol_id=allele_protocol_id,
            locus_set_id=locus_set_id,
            n_loci=n_loci,
            format=enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            content_hash=model.SeqProfile.get_allele_profile_hash(allele_ids),  # type: ignore[arg-type]
            content=base64.b64encode(
                b"".join(NULL_ID.bytes if x is None else x.bytes for x in allele_ids)
            ).decode("ascii"),
            sample_id=sample.id,
        )
        samples.append(sample)
        profiles.append(profile)
    return profiles, samples


def _extract_protocol_info(
    db: dict,
) -> tuple[model.Protocol, UUID, UUID, int]:
    """Return (distance_protocol, allele_protocol_id, locus_set_id, n_loci)."""
    protocols = list(db[model.Protocol].values())
    dist_proto = next(
        p for p in protocols if p.protocol_type == enum.ProtocolType.SEQ_DISTANCE
    )
    allele_proto = next(
        p
        for p in protocols
        if p.protocol_type == enum.ProtocolType.SEQ_PROFILE
        and p.seq_profile_type == enum.SeqProfileType.ALLELE
    )
    locus_set = next(iter(db[model.LocusSet].values()))
    return dist_proto, cast(UUID, allele_proto.id), cast(UUID, locus_set.id), N_LOCI


# ── Pyinstrument segment extractor ───────────────────────────────────────────

# Function-name sets used to bucket profiler time into segments. Names must
# match the actual function names in calculate_seq_distance.py.
_READ_FNS = frozenset({"iter_seq_distances", "iter_seq_distance_essentials"})
_DECODE_FNS = frozenset(
    {
        "_decode_profile",
        "get_allele_id_bytes",
        "get_allele_array",
        "_parse_nextclade_profile_content",
    }
)
_COMPARE_FNS = frozenset(
    {
        "_calculate_distance_for_decoded_profile_pair",
        "_hamming_allele_numpy",
        "_hamming_allele_numpy_batch",
    }
)
_WRITE_FNS = frozenset(
    {"bulk_update_seq_distance_content", "bulk_insert_seq_distance_pairs"}
)


def _extract_segments(frame_data: dict[str, Any]) -> dict[str, float]:
    """Walk pyinstrument JSON frame tree; accumulate time by function role."""
    totals: dict[str, float] = {k: 0.0 for k in ("read", "decode", "compare", "write")}

    def _walk(frame: dict[str, Any]) -> None:
        fn = frame.get("function", "")
        t = frame.get("time", 0.0)
        if fn in _READ_FNS:
            totals["read"] += t
        elif fn in _DECODE_FNS:
            totals["decode"] += t
        elif fn in _COMPARE_FNS:
            totals["compare"] += t
        elif fn in _WRITE_FNS:
            totals["write"] += t
        for child in frame.get("children") or []:
            _walk(child)

    _walk(frame_data.get("root_frame", {}))
    return {f"{k}_s": v for k, v in totals.items()}


# ── Chart helpers ─────────────────────────────────────────────────────────────

_VARIANT_NAMES = [v["name"] for v in VARIANTS]
_CHART_COLORS = ["#4878D0", "#EE854A", "#6ACC65", "#D65F5F"]
# Colors for n_existing groups (used across all simple bar charts)
_N_EX_COLORS = ["#4878D0", "#EE854A", "#6ACC65", "#D65F5F", "#956CB4"]


def _max_n_ex_for_repo(results: list[dict], repo: str) -> int:
    """Return the largest n_existing actually present in results for this repo."""
    return max(r["n_existing"] for r in results if r["repo"] == repo)


def _n_ex_for_repo(results: list[dict], repo: str) -> list[int]:
    """Return all n_existing values present for this repo, sorted ascending."""
    return sorted({r["n_existing"] for r in results if r["repo"] == repo})


def _fmt_s(v: float) -> str:
    """Format a duration: use ms below 1 s, otherwise seconds."""
    if v == 0.0:
        return "0"
    if v < 1.0:
        return f"{v * 1000:.0f}ms"
    return f"{v:.1f}s"


def _grouped_bars(
    ax: Any,
    results: list[dict],
    metric: str,
    repo: str,
    n_new: int,
    n_ex_values: list[int],
) -> None:
    """Draw grouped bars: one group per variant, one bar per n_existing."""
    x = np.arange(len(_VARIANT_NAMES))
    n_groups = len(n_ex_values)
    width = 0.8 / max(n_groups, 1)
    offsets = (np.arange(n_groups) - (n_groups - 1) / 2) * width
    for ex_idx, n_ex in enumerate(n_ex_values):
        vals = _filter(results, repo, n_ex, n_new)
        bars = ax.bar(
            x + offsets[ex_idx], vals, width,
            color=_N_EX_COLORS[ex_idx % len(_N_EX_COLORS)],
            label=f"n_ex={n_ex}",
        )
        ax.bar_label(bars, labels=[_fmt_s(v) for v in vals],
                     padding=2, fontsize=6, rotation=90)
    ax.set_xticks(x)
    ax.set_xticklabels(_VARIANT_NAMES, rotation=30, ha="right")
    ax.legend(fontsize=7)


def _filter(
    results: list[dict],
    repo: str,
    n_ex: int,
    n_new: int,
) -> list[float]:
    """Return values for each variant in VARIANTS order."""
    out = []
    for v in _VARIANT_NAMES:
        row = next(
            (
                r
                for r in results
                if r["variant"] == v
                and r["repo"] == repo
                and r["n_existing"] == n_ex
                and r["n_new"] == n_new
            ),
            None,
        )
        out.append(row["wall_s"] if row else 0.0)
    return out


def _plot_total_duration(results: list[dict], out: Path) -> None:  # pragma: no cover
    if not _HAS_MATPLOTLIB:
        return
    repos = sorted({r["repo"] for r in results})
    n_new_values = sorted({r["n_new"] for r in results})
    fig, axes = plt.subplots(
        len(n_new_values), len(repos),
        figsize=(7 * len(repos), 5 * len(n_new_values)), sharey="row"
    )
    if len(n_new_values) == 1:
        axes = [axes]
    if len(repos) == 1:
        axes = [[ax] for ax in axes]
    for row_idx, n_new in enumerate(n_new_values):
        for col_idx, repo in enumerate(repos):
            ax = axes[row_idx][col_idx]
            n_ex_values = _n_ex_for_repo(results, repo)
            _grouped_bars(ax, results, "wall_s", repo, n_new, n_ex_values)
            ax.set_title(f"{repo} n_new={n_new}")
            ax.set_ylabel("seconds")
    fig.suptitle("Total wall time")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def _plot_per_profile(results: list[dict], out: Path) -> None:  # pragma: no cover
    if not _HAS_MATPLOTLIB:
        return
    repos = sorted({r["repo"] for r in results})
    n_new_values = sorted({r["n_new"] for r in results})
    fig, axes = plt.subplots(
        len(n_new_values), len(repos),
        figsize=(7 * len(repos), 5 * len(n_new_values)), sharey="row"
    )
    if len(n_new_values) == 1:
        axes = [axes]
    if len(repos) == 1:
        axes = [[ax] for ax in axes]
    for row_idx, n_new in enumerate(n_new_values):
        for col_idx, repo in enumerate(repos):
            ax = axes[row_idx][col_idx]
            n_ex_values = _n_ex_for_repo(results, repo)
            x = np.arange(len(_VARIANT_NAMES))
            n_groups = len(n_ex_values)
            width = 0.8 / max(n_groups, 1)
            offsets = (np.arange(n_groups) - (n_groups - 1) / 2) * width
            for ex_idx, n_ex in enumerate(n_ex_values):
                vals = [v / max(n_new, 1) for v in _filter(results, repo, n_ex, n_new)]
                bars = ax.bar(
                    x + offsets[ex_idx], vals, width,
                    color=_N_EX_COLORS[ex_idx % len(_N_EX_COLORS)],
                    label=f"n_ex={n_ex}",
                )
                ax.bar_label(bars, labels=[_fmt_s(v) for v in vals],
                             padding=2, fontsize=6, rotation=90)
            ax.set_title(f"{repo} n_new={n_new}")
            ax.set_ylabel("seconds / profile")
            ax.set_xticks(x)
            ax.set_xticklabels(_VARIANT_NAMES, rotation=30, ha="right")
            ax.legend(fontsize=7)
    fig.suptitle("Wall time per new profile")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def _plot_segments(results: list[dict], out: Path) -> None:
    """Stacked bar: read / decode / compare / write per variant per repo × n_existing."""
    if not _HAS_MATPLOTLIB:  # pragma: no cover
        return
    repos = sorted({r["repo"] for r in results})
    n_new = max(r["n_new"] for r in results)
    seg_keys = ["read_s", "decode_s", "compare_s", "write_s"]
    seg_labels = ["read", "decode", "compare", "write"]

    # One column per (repo, n_existing) combination
    cols = [(repo, n_ex) for repo in repos for n_ex in _n_ex_for_repo(results, repo)]
    fig, axes = plt.subplots(1, len(cols), figsize=(7 * len(cols), 5), sharey=True)
    if len(cols) == 1:
        axes = [axes]
    for ax, (repo, n_ex) in zip(axes, cols):
        bottoms = np.zeros(len(_VARIANT_NAMES))
        for seg, label, color in zip(seg_keys, seg_labels, _CHART_COLORS):
            heights = []
            for vname in _VARIANT_NAMES:
                row = next(
                    (
                        r
                        for r in results
                        if r["variant"] == vname
                        and r["repo"] == repo
                        and r["n_existing"] == n_ex
                        and r["n_new"] == n_new
                    ),
                    None,
                )
                heights.append(row[seg] if row else 0.0)
            ax.bar(
                _VARIANT_NAMES, heights, bottom=bottoms, label=label, color=color
            )
            bottoms += np.array(heights)
        totals = []
        for vname in _VARIANT_NAMES:
            row = next(
                (
                    r
                    for r in results
                    if r["variant"] == vname
                    and r["repo"] == repo
                    and r["n_existing"] == n_ex
                    and r["n_new"] == n_new
                ),
                None,
            )
            totals.append(row["wall_s"] if row else 0.0)
        for x_pos, total in enumerate(totals):
            ax.text(x_pos, bottoms[x_pos] + 0.01 * max(bottoms), _fmt_s(total),
                    ha="center", va="bottom", fontsize=7)
        ax.set_title(f"{repo} ex={n_ex} n_new={n_new}")
        ax.set_ylabel("seconds")
        ax.set_xticks(range(len(_VARIANT_NAMES)))
        ax.set_xticklabels(_VARIANT_NAMES, rotation=30, ha="right")
        ax.legend()
    fig.suptitle("Time breakdown by segment")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def _plot_retrieve(results: list[dict], out: Path) -> None:  # pragma: no cover
    if not _HAS_MATPLOTLIB:
        return
    repos = sorted({r["repo"] for r in results})
    n_new_values = sorted({r["n_new"] for r in results})
    fig, axes = plt.subplots(
        len(n_new_values), len(repos),
        figsize=(7 * len(repos), 5 * len(n_new_values)), sharey="row"
    )
    if len(n_new_values) == 1:
        axes = [axes]
    if len(repos) == 1:
        axes = [[ax] for ax in axes]
    for row_idx, n_new in enumerate(n_new_values):
        for col_idx, repo in enumerate(repos):
            ax = axes[row_idx][col_idx]
            n_ex_values = _n_ex_for_repo(results, repo)
            x = np.arange(len(_VARIANT_NAMES))
            n_groups = len(n_ex_values)
            width = 0.8 / max(n_groups, 1)
            offsets = (np.arange(n_groups) - (n_groups - 1) / 2) * width
            for ex_idx, n_ex in enumerate(n_ex_values):
                vals = []
                for vname in _VARIANT_NAMES:
                    row = next(
                        (
                            r
                            for r in results
                            if r["variant"] == vname
                            and r["repo"] == repo
                            and r["n_existing"] == n_ex
                            and r["n_new"] == n_new
                        ),
                        None,
                    )
                    vals.append(row["retrieve_wall_s"] if row else 0.0)
                bars = ax.bar(
                    x + offsets[ex_idx], vals, width,
                    color=_N_EX_COLORS[ex_idx % len(_N_EX_COLORS)],
                    label=f"n_ex={n_ex}",
                )
                ax.bar_label(bars, labels=[_fmt_s(v) for v in vals],
                             padding=2, fontsize=6, rotation=90)
            ax.set_title(f"{repo} n_new={n_new}")
            ax.set_ylabel("seconds")
            ax.set_xticks(x)
            ax.set_xticklabels(_VARIANT_NAMES, rotation=30, ha="right")
            ax.legend(fontsize=7)
    fig.suptitle("RetrieveSimilarProfiles wall time (10 query profiles)")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


# ── Session fixture: generate charts after all tests finish ──────────────────


@pytest.fixture(scope="session", autouse=True)
def generate_benchmark_charts() -> Any:
    yield
    if not _RESULTS:
        return
    output_dir = Path("test/output")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "benchmark_lsp3477_results.json", "w") as fh:
        json.dump(_RESULTS, fh, indent=2)
    if _HAS_MATPLOTLIB:
        _plot_total_duration(_RESULTS, output_dir / "benchmark_lsp3477_total.png")
        _plot_per_profile(_RESULTS, output_dir / "benchmark_lsp3477_per_profile.png")
        _plot_segments(_RESULTS, output_dir / "benchmark_lsp3477_segments.png")
        _plot_retrieve(_RESULTS, output_dir / "benchmark_lsp3477_retrieve.png")


# ── Parametrization ───────────────────────────────────────────────────────────

_PARAMS = [
    (v, rt, n_ex, n_new)
    for v in VARIANTS
    for rt in REPO_TYPES
    for n_ex in N_EXISTING
    for n_new in N_NEW
]
_IDS = [
    f"{v['name']}-{rt.value}-ex{n_ex}-n{n_new}"
    for v, rt, n_ex, n_new in _PARAMS
]


# ── Main benchmark class (DICT + SA_SQLITE) ───────────────────────────────────


@pytest.mark.performance
class TestDistanceOptimizationBenchmark:
    """Compare six distance-calculation variants on DICT and SA_SQLITE repos.

    The setup fixture builds one base DICT db and one base SQLite per
    n_existing. Each test variant gets a fresh copy so results are comparable:
    - DICT: shallow-copy the base db dict, inject n_new profiles, create repo.
    - SA_SQLITE: shutil.copy the base SQLite, insert n_new profiles, run test,
      then delete the temp file.
    """

    entities: list
    base_dbs: dict[int, dict]
    dist_protocols: dict[int, model.Protocol]
    new_profiles: dict[tuple[int, int], tuple[list[model.SeqProfile], list[model.Sample]]]
    base_sqlite_paths: dict[int, Path]

    @pytest.fixture(scope="module", autouse=True)
    def setup(self, env: Env) -> None:
        BENCHMARK_DATA_DIR.mkdir(parents=True, exist_ok=True)

        user_id = cast(UUID, env.get_root_user().id)
        entities = env.app.domain.get_dag_sorted_entities(
            service_type=enum.ServiceType.SEQ, persistable=True
        )
        type(self).entities = entities

        type(self).base_dbs = {}
        type(self).dist_protocols = {}
        type(self).new_profiles = {}
        type(self).base_sqlite_paths = {}

        for n_ex in N_EXISTING:
            db = generate_scale_test_db(
                n_loci=N_LOCI, n_existing=n_ex, seed=n_ex
            )
            dist_proto, allele_proto_id, locus_set_id, n_loci = _extract_protocol_info(db)

            type(self).base_dbs[n_ex] = db
            type(self).dist_protocols[n_ex] = dist_proto

            # Pre-generate new profiles for each n_new (deterministic seeds)
            for n_new in N_NEW:
                profs, samps = _generate_new_profiles(
                    n_new, allele_proto_id, locus_set_id, n_loci, seed=n_ex + n_new
                )
                type(self).new_profiles[(n_ex, n_new)] = (profs, samps)

            # Base SQLite — created once, reused across benchmark runs.
            # Guard against a partially-written file: if a previous run created
            # the schema but the fill transaction was never committed (e.g. the
            # process was killed), the file exists and has non-zero size but
            # contains no rows.  In that case we delete it and start fresh.
            sqlite_path = BENCHMARK_DATA_DIR / f"bench_base_{n_ex}.sqlite"
            reuse = sqlite_path.exists() and sqlite_path.stat().st_size > 0
            base_sa_repo = create_sqlite_repository(
                sqlite_path, entities, recreate_sqlite_file=not reuse
            )
            if reuse and count_seq_profiles(base_sa_repo) != n_ex:
                sqlite_path.unlink(missing_ok=True)
                base_sa_repo = create_sqlite_repository(
                    sqlite_path, entities, recreate_sqlite_file=True
                )
                reuse = False
            if not reuse:
                base_dict_repo = create_dict_repository(
                    pickle_file=None, db=db, entities=entities
                )
                fill_empty_sqlite_repository(
                    base_dict_repo, base_sa_repo, entities, user_id
                )
            type(self).base_sqlite_paths[n_ex] = sqlite_path

    @pytest.mark.parametrize("variant,repo_type,n_existing,n_new", _PARAMS, ids=_IDS)
    def test_variant(
        self,
        env: Env,
        variant: dict,
        repo_type: enum.RepositoryType,
        n_existing: int,
        n_new: int,
    ) -> None:
        new_profs, new_samps = self.new_profiles[(n_existing, n_new)]
        user_id = env.get_root_user().id
        temp_sqlite: Path | None = None

        if repo_type == enum.RepositoryType.DICT:
            # Shallow-copy so each variant starts with the same base state.
            # dict(v) creates new dict objects; the Distance/DistancePair dicts
            # are empty so writes never conflict with base data.
            fresh_db = {k: dict(v) for k, v in self.base_dbs[n_existing].items()}
            for s in new_samps:
                fresh_db[model.Sample][s.id] = s
            for p in new_profs:
                fresh_db[model.SeqProfile][p.id] = p
            repo: Any = create_dict_repository(
                pickle_file=None, db=fresh_db, entities=self.entities
            )
        else:
            # Copy base SQLite, insert new profiles (no SeqDistance records),
            # then run the timed test. Temp file is deleted in the finally block.
            base_path = self.base_sqlite_paths[n_existing]
            temp_sqlite = (
                BENCHMARK_DATA_DIR
                / f"bench_run_{variant['name']}_{n_existing}_{n_new}.sqlite"
            )
            shutil.copy(base_path, temp_sqlite)
            repo = create_sqlite_repository(
                temp_sqlite, self.entities, recreate_sqlite_file=False
            )
            with repo.uow() as uow:
                repo.crud(
                    uow, user_id, model.Sample, CrudOperation.CREATE_SOME, objs=new_samps
                )
                repo.crud(
                    uow, user_id, model.SeqProfile, CrudOperation.CREATE_SOME, objs=new_profs
                )

        set_service_repository(env, repo)

        try:
            cmd = command.CalculateSeqDistancesForNewProfilesCommand(
                user=env.get_root_user(),
                seq_profiles=new_profs,
                existing_chunk_size=EXISTING_CHUNK_SIZE,
                use_row_per_pair=variant["pair"],
                use_numpy_allele=variant["numpy"],
                use_batch_new_profiles=variant["batch"],
            )

            profiler = pyinstrument.Profiler()
            profiler.start()
            t0 = perf_counter()
            env.app.handle(cmd)
            wall_s = perf_counter() - t0
            profiler.stop()

            frame_data = json.loads(profiler.output(renderer=JSONRenderer()))
            segments = _extract_segments(frame_data)

            # Retrieve sub-benchmark: query similar profiles for up to 10 new IDs.
            retrieve_profile_ids = [
                cast(UUID, p.id) for p in new_profs[: min(10, len(new_profs))]
            ]
            retrieve_cmd = command.RetrieveSimilarProfilesCommand(
                user=env.get_root_user(),
                protocol_id=cast(UUID, self.dist_protocols[n_existing].id),
                profile_ids=retrieve_profile_ids,
                max_distance=RETRIEVE_MAX_DISTANCE,
                use_row_per_pair=variant["pair"],
            )
            t_r = perf_counter()
            env.app.handle(retrieve_cmd)
            retrieve_wall_s = perf_counter() - t_r

        finally:
            if temp_sqlite is not None:
                temp_sqlite.unlink(missing_ok=True)

        _RESULTS.append(
            {
                "variant": variant["name"],
                "repo": repo_type.value,
                "n_existing": n_existing,
                "n_new": n_new,
                "wall_s": wall_s,
                "per_profile_s": wall_s / max(n_new, 1),
                "retrieve_wall_s": retrieve_wall_s,
                **segments,
            }
        )
        print(
            f"\n{variant['name']} {repo_type.value} ex={n_existing} n={n_new}: "
            f"{wall_s:.2f}s  ({wall_s / max(n_new, 1):.3f}s/profile)"
        )


# ── MSSQL variant (optional) ──────────────────────────────────────────────────


_MSSQL_PARAMS = [(v, n_new) for v in VARIANTS for n_new in N_NEW]
_MSSQL_IDS = [f"{v['name']}-mssql-n{n}" for v, n in _MSSQL_PARAMS]


@pytest.mark.performance
@pytest.mark.mssql
class TestDistanceOptimizationBenchmarkMssql:
    """Same six variants against a SQL Server container.

    Set SEQDB_MSSQL_TEST_URL to enable (see the existing scale test file
    for the docker run command and URL format). Only tested at n_existing=5000.
    Results are appended to _RESULTS with repo="SA_SQL".
    """

    entities: list
    dist_protocol: model.Protocol
    new_profiles: dict[tuple[str, int], tuple[list[model.SeqProfile], list[model.Sample]]]
    mssql_repo: Any
    base_db: dict

    _N_EXISTING_MSSQL = 5000

    @pytest.fixture(scope="module", autouse=True)
    def setup(self, env: Env) -> None:
        mssql_url = os.environ.get(MSSQL_URL_ENV)
        if not mssql_url:
            pytest.skip(f"{MSSQL_URL_ENV} not set")

        user_id = cast(UUID, env.get_root_user().id)
        n_ex = self._N_EXISTING_MSSQL
        entities = env.app.domain.get_dag_sorted_entities(
            service_type=enum.ServiceType.SEQ, persistable=True
        )
        type(self).entities = entities

        db = generate_scale_test_db(n_loci=N_LOCI, n_existing=n_ex, seed=n_ex)
        dist_proto, allele_proto_id, locus_set_id, n_loci = _extract_protocol_info(db)
        type(self).base_db = db
        type(self).dist_protocol = dist_proto

        type(self).new_profiles = {}
        for v_idx, variant in enumerate(VARIANTS):
            for n_new in N_NEW:
                profs, samps = _generate_new_profiles(
                    n_new, allele_proto_id, locus_set_id, n_loci,
                    seed=n_ex + n_new + v_idx * 10_000,
                )
                type(self).new_profiles[(variant["name"], n_new)] = (profs, samps)

        mssql_repo = create_mssql_repository(mssql_url, entities)
        if count_seq_profiles(mssql_repo) == 0:
            dict_repo = create_dict_repository(
                pickle_file=None, db=db, entities=entities
            )
            fill_empty_sqlite_repository(dict_repo, mssql_repo, entities, user_id)
        type(self).mssql_repo = mssql_repo

    @pytest.mark.parametrize("variant,n_new", _MSSQL_PARAMS, ids=_MSSQL_IDS)
    def test_variant(self, env: Env, variant: dict, n_new: int) -> None:
        n_ex = self._N_EXISTING_MSSQL
        new_profs, new_samps = self.new_profiles[(variant["name"], n_new)]
        user_id = env.get_root_user().id

        # Insert new profiles for this variant, then clean up afterwards so
        # every variant runs against the same n_existing baseline and re-runs
        # do not produce duplicate-key errors.
        with self.mssql_repo.uow() as uow:
            self.mssql_repo.crud(
                uow, user_id, model.Sample, CrudOperation.CREATE_SOME, objs=new_samps
            )
            self.mssql_repo.crud(
                uow, user_id, model.SeqProfile, CrudOperation.CREATE_SOME, objs=new_profs
            )

        set_service_repository(env, self.mssql_repo)

        try:
            cmd = command.CalculateSeqDistancesForNewProfilesCommand(
                user=env.get_root_user(),
                seq_profiles=new_profs,
                existing_chunk_size=EXISTING_CHUNK_SIZE,
                use_row_per_pair=variant["pair"],
                use_numpy_allele=variant["numpy"],
                use_batch_new_profiles=variant["batch"],
            )

            profiler = pyinstrument.Profiler()
            profiler.start()
            t0 = perf_counter()
            env.app.handle(cmd)
            wall_s = perf_counter() - t0
            profiler.stop()

            frame_data = json.loads(profiler.output(renderer=JSONRenderer()))
            segments = _extract_segments(frame_data)

            retrieve_profile_ids = [
                cast(UUID, p.id) for p in new_profs[: min(10, len(new_profs))]
            ]
            retrieve_cmd = command.RetrieveSimilarProfilesCommand(
                user=env.get_root_user(),
                protocol_id=cast(UUID, self.dist_protocol.id),
                profile_ids=retrieve_profile_ids,
                max_distance=RETRIEVE_MAX_DISTANCE,
                use_row_per_pair=variant["pair"],
            )
            t_r = perf_counter()
            env.app.handle(retrieve_cmd)
            retrieve_wall_s = perf_counter() - t_r

        finally:
            # Delete in FK-safe order:
            #   SeqDistance / SeqDistancePair → SeqProfile → Sample
            new_prof_ids = [cast(UUID, p.id) for p in new_profs]
            new_samp_ids = [cast(UUID, s.id) for s in new_samps]
            new_prof_id_set = set(new_prof_ids)
            with self.mssql_repo.uow() as uow:
                if variant["pair"]:
                    all_pairs = self.mssql_repo.crud(
                        uow, user_id, model.SeqDistancePair,
                        CrudOperation.READ_ALL, return_copy=False,
                    )
                    pair_ids = [
                        cast(UUID, r.id) for r in all_pairs
                        if r.profile_id_a in new_prof_id_set
                        or r.profile_id_b in new_prof_id_set
                    ]
                    if pair_ids:
                        self.mssql_repo.crud(
                            uow, user_id, model.SeqDistancePair,
                            CrudOperation.DELETE_SOME, obj_ids=pair_ids,
                        )
                else:
                    all_dists = self.mssql_repo.crud(
                        uow, user_id, model.SeqDistance,
                        CrudOperation.READ_ALL, return_copy=False,
                    )
                    dist_ids = [
                        cast(UUID, r.id) for r in all_dists
                        if r.seq_profile_id in new_prof_id_set
                    ]
                    if dist_ids:
                        self.mssql_repo.crud(
                            uow, user_id, model.SeqDistance,
                            CrudOperation.DELETE_SOME, obj_ids=dist_ids,
                        )
                self.mssql_repo.crud(
                    uow, user_id, model.SeqProfile,
                    CrudOperation.DELETE_SOME, obj_ids=new_prof_ids,
                )
                self.mssql_repo.crud(
                    uow, user_id, model.Sample,
                    CrudOperation.DELETE_SOME, obj_ids=new_samp_ids,
                )

        _RESULTS.append(
            {
                "variant": variant["name"],
                "repo": "SA_SQL",
                "n_existing": n_ex,
                "n_new": n_new,
                "wall_s": wall_s,
                "per_profile_s": wall_s / max(n_new, 1),
                "retrieve_wall_s": retrieve_wall_s,
                **segments,
            }
        )
        print(
            f"\n{variant['name']} SA_SQL ex={n_ex} n={n_new}: "
            f"{wall_s:.2f}s  ({wall_s / max(n_new, 1):.3f}s/profile)"
        )
