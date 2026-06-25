"""
Benchmark comparing blob_numpy_batch vs pair_numpy_batch for LSP-3477.

Both variants use numpy vectorisation and batched new-profile comparison.
They are timed on DICT and SA_SQLITE repositories at multiple scales. Each
variant runs on a FRESH copy of the repository so results are comparable.

Profiles are generated with realistic distance distributions (colleague's
ColdSampleGenerator approach): per-locus mutation probabilities sampled from
Uniform(0, _LOCUS_MAX_MUTATION_PROB). This means most pairs exceed
max_stored_distance=20 (cross-strain), while same-strain pairs cluster within
the threshold — matching the production distance distribution.

Large SQLite base files are stored in BENCHMARK_DATA_DIR (D: drive). The
filename includes _BENCH_VERSION so changing generation parameters
automatically invalidates old cached files. Old files can be deleted manually.

Each test cell saves a pyinstrument HTML flame graph to RUN_DIR/profiles/.

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
from datetime import datetime
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
from gen_epix.util import chunk_list
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
# Keep SQLite base files on the native WSL2 filesystem to avoid the 9P
# cross-filesystem overhead of /mnt/d (Windows drive). That overhead
# benchmarked at ~21 MB/s (3s per 1000-profile chunk × 5 chunks = 15s
# untracked "rest") and masked the real algorithmic differences.
BENCHMARK_DATA_DIR = Path("/home/paulessers/data/lsp-3477-benchmark")

# ── Benchmark parameters ────────────────────────────────────────────────────
MSSQL_URL_ENV = "SEQDB_MSSQL_TEST_URL"

# existing_chunk_size for _calculate_and_store_distances (match prod default)
EXISTING_CHUNK_SIZE = 1000

# pyodbc raises ODBC 07002 when a single parameterized query has more than
# ~2100 bound parameters. Chunk DELETE_SOME calls to stay well under that.
_DELETE_CHUNK_SIZE = 500

# Production retrieve threshold: ~50 near-neighbours per case.
RETRIEVE_MAX_DISTANCE = 5

# Version tag baked into SQLite filenames. Bump when changing profile
# generation parameters so old cached files are never reused silently.
_BENCH_VERSION = "v4"

# max_stored_distance passed to generate_scale_test_db (mirrors prod value).
_MAX_STORED_DISTANCE = 20.0

# Colleague's ColdSampleGenerator approach: per-locus mutation probability
# sampled from Uniform(0, _LOCUS_MAX_MUTATION_PROB). 0.003 → expected
# within-strain pairwise distance ~9, so most pairs fall within 20 loci.
_LOCUS_MAX_MUTATION_PROB = 0.003
_NULL_PROB = 0.005
_PROFILE_GEN_SEED = 42

# Target within-cluster size: each new profile has ~_CLUSTER_SIZE stored
# neighbours. n_clusters = max(1, n_existing // _CLUSTER_SIZE) is derived
# per scale so the stored pair count stays ~constant as n_existing grows.
_CLUSTER_SIZE = 50

N_EXISTING = [1000, 5000]
N_NEW = [10, 50, 100, 500]
N_LOCI = 3000

VARIANTS = [
    {"name": "blob_original",                "pair": False, "numpy": False, "batch": False, "bulk": False, "int32_vocab": False, "flipped": False},
    {"name": "blob_numpy_batch",             "pair": False, "numpy": True, "batch": True,  "bulk": False, "int32_vocab": False, "flipped": False},
    {"name": "blob_int32_vocab",             "pair": False, "numpy": True, "batch": False, "bulk": False, "int32_vocab": True,  "flipped": False},
    # {"name": "pair_numpy_batch_bulk",        "pair": True,  "numpy": True, "batch": True,  "bulk": True,  "int32_vocab": False, "flipped": False},
    # {"name": "pair_int32_vocab_bulk",        "pair": True,  "numpy": True, "batch": False, "bulk": True,  "int32_vocab": True,  "flipped": False},
    # {"name": "pair_int32_vocab_bulk_flipped","pair": True,  "numpy": True, "batch": False, "bulk": True,  "int32_vocab": True,  "flipped": True},
]
REPO_TYPES = [enum.RepositoryType.SA_SQLITE]

# ── Per-run output directory ─────────────────────────────────────────────────
# Created once at import time so every cell in the session lands in the same
# directory. Charts and JSON summary are written here; flame graphs go in
# profiles/ subdirectory (one HTML per cell).
RUN_DIR = Path("test/output") / (
    datetime.now().strftime("%Y%m%d_%H%M%S") + "_seq_distance_optimisation"
)

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


# ── Realistic profile generation helpers ─────────────────────────────────────


def _init_profile_generator(
    n_loci: int,
    n_clusters: int,
) -> tuple[np.ndarray, list[list[UUID]]]:
    """Return (locus_probs, cluster_refs) for multi-cluster realistic profiles.

    locus_probs[i] is the per-locus mutation probability (shared across all
    clusters). cluster_refs[k] is the reference allele list for cluster k;
    cluster references are fully independent (random UUIDs) so cross-cluster
    pairs always exceed max_stored_distance.

    Within-cluster expected pairwise distance ≈ 9 loci with
    _LOCUS_MAX_MUTATION_PROB=0.003. Cross-cluster distance ≈ n_loci (3000).
    """
    rng = np.random.default_rng(_PROFILE_GEN_SEED)
    locus_probs = rng.uniform(0.0, _LOCUS_MAX_MUTATION_PROB, size=n_loci)
    cluster_refs: list[list[UUID]] = []
    for _ in range(n_clusters):
        raw = rng.integers(0, 256, size=(n_loci, 16), dtype=np.uint8)
        cluster_refs.append([UUID(bytes=bytes(row)) for row in raw])
    return locus_probs, cluster_refs


def _make_realistic_profiles(
    n: int,
    allele_protocol_id: UUID,
    locus_set_id: UUID,
    n_loci: int,
    cluster_refs: list[list[UUID]],
    locus_probs: np.ndarray,
    seed: int = 0,
) -> tuple[list[model.SeqProfile], list[model.Sample]]:
    """Generate n realistic SeqProfile + Sample pairs across clusters.

    Profiles are assigned round-robin to clusters so each cluster gets an
    equal share. Within a cluster, each locus mutates with probability
    locus_probs[i]. Cross-cluster pairs exceed max_stored_distance and are
    never stored.
    """
    import random as _rnd

    id_rng = _rnd.Random(seed)
    np_rng = np.random.default_rng(seed)
    n_clusters = len(cluster_refs)

    def _uuid() -> UUID:
        return UUID(int=id_rng.getrandbits(128))

    profiles: list[model.SeqProfile] = []
    samples: list[model.Sample] = []
    for i in range(n):
        reference_allele_ids = cluster_refs[i % n_clusters]
        alleles = list(reference_allele_ids)
        mutate_mask = np_rng.random(n_loci) < locus_probs
        null_mask = np_rng.random(n_loci) < _NULL_PROB
        for j in np.where(mutate_mask)[0]:
            alleles[j] = _uuid()
        for j in np.where(null_mask)[0]:
            alleles[j] = NULL_ID
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
            content_hash=model.SeqProfile.get_allele_profile_hash(alleles),  # type: ignore[arg-type]
            content=base64.b64encode(
                b"".join(x.bytes for x in alleles)
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
# SeqDistance blob reads (blob path). Profile reads (step 4a) are tracked
# separately under profile_read_s via _PROFILE_READ_FNS.
_READ_FNS = frozenset(
    {
        "iter_seq_distances",
        "iter_seq_distance_essentials",
        "iter_seq_distance_profile_ids",  # blob path: load existing profile ID set
    }
)
_PROFILE_READ_FNS = frozenset({"read_some"})
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
        "_hamming_allele_int32_batch",
        "_encode_to_int32",
    }
)
_WRITE_FNS = frozenset(
    {
        "update_some_seq_distance_content",  # blob UPDATE existing SeqDistance
        "bulk_insert_seq_distance_pairs",    # pair Core executemany path
        "create_some",                       # pair ORM path + blob CREATE new
    }
)


def _extract_segments(frame_data: dict[str, Any]) -> dict[str, float]:
    """Walk pyinstrument JSON/HTML frame tree; accumulate time by function role.

    The HTML renderer uses {identifier, time, children} nodes; the JSON
    renderer uses {function, time, children}. Both are handled here.
    """
    totals: dict[str, float] = {
        k: 0.0 for k in ("read", "profile_read", "decode", "compare", "write")
    }

    def _walk(frame: dict[str, Any]) -> None:
        # HTML renderer stores "function_name /path lineN" in 'identifier';
        # JSON renderer stores the bare name in 'function'.
        raw_id = frame.get("identifier") or frame.get("function") or ""
        fn = raw_id.split(" ")[0]  # take just the function name
        t = frame.get("time", 0.0)
        if fn in _READ_FNS:
            totals["read"] += t
        elif fn in _PROFILE_READ_FNS:
            totals["profile_read"] += t
        elif fn in _DECODE_FNS:
            totals["decode"] += t
        elif fn in _COMPARE_FNS:
            totals["compare"] += t
        elif fn in _WRITE_FNS:
            totals["write"] += t
        for child in frame.get("children") or []:
            _walk(child)

    # HTML renderer wraps data in {"session": ..., "frame_tree": ...};
    # JSON renderer wraps it in {"root_frame": ...}.
    root = (
        frame_data.get("frame_tree")
        or frame_data.get("root_frame")
        or {}
    )
    _walk(root)
    return {f"{k}_s": v for k, v in totals.items()}


# ── Chart helpers ─────────────────────────────────────────────────────────────

_VARIANT_NAMES = [v["name"] for v in VARIANTS]
_CHART_COLORS = ["#4878D0", "#956CB4", "#EE854A", "#6ACC65", "#D65F5F", "#BBBBBB"]
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
    """Stacked bar: read / decode / compare / write per variant.

    Rows = n_new values (all present in results), columns = (repo, n_existing).
    """
    if not _HAS_MATPLOTLIB:  # pragma: no cover
        return
    repos = sorted({r["repo"] for r in results})
    n_new_values = sorted({r["n_new"] for r in results})
    seg_keys = [
        "read_s", "profile_read_s", "decode_s", "compare_s", "write_s", "rest_s"
    ]
    seg_labels = ["read (dist)", "profile_read", "decode", "compare", "write", "rest"]

    cols = [(repo, n_ex) for repo in repos for n_ex in _n_ex_for_repo(results, repo)]
    n_rows = len(n_new_values)
    n_cols = len(cols)
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(7 * n_cols, 5 * n_rows),
        sharey="row",
        squeeze=False,
    )
    for row_idx, n_new in enumerate(n_new_values):
        for col_idx, (repo, n_ex) in enumerate(cols):
            ax = axes[row_idx][col_idx]
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
            for x_pos, vname in enumerate(_VARIANT_NAMES):
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
                total = row["wall_s"] if row else 0.0
                ax.text(
                    x_pos, bottoms[x_pos] + 0.01 * max(bottoms),
                    _fmt_s(total), ha="center", va="bottom", fontsize=7,
                )
            ax.set_title(f"{repo} ex={n_ex} n_new={n_new}")
            ax.set_ylabel("seconds")
            ax.set_xticks(range(len(_VARIANT_NAMES)))
            ax.set_xticklabels(_VARIANT_NAMES, rotation=30, ha="right")
            if col_idx == 0:
                ax.legend(fontsize=7)
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


def _plot_lines_per_variant(results: list[dict], out: Path) -> None:  # pragma: no cover
    """Line chart: one subplot per variant, one line per n_existing, x = n_new."""
    if not _HAS_MATPLOTLIB:
        return
    repos = sorted({r["repo"] for r in results})
    n_new_values = sorted({r["n_new"] for r in results})
    fig, axes = plt.subplots(
        len(repos), len(_VARIANT_NAMES),
        figsize=(5 * len(_VARIANT_NAMES), 4 * len(repos)),
        sharey="row", squeeze=False,
    )
    for row_idx, repo in enumerate(repos):
        n_ex_values = _n_ex_for_repo(results, repo)
        for col_idx, vname in enumerate(_VARIANT_NAMES):
            ax = axes[row_idx][col_idx]
            for ex_idx, n_ex in enumerate(n_ex_values):
                ys = [
                    next(
                        (r["wall_s"] for r in results
                         if r["variant"] == vname and r["repo"] == repo
                         and r["n_existing"] == n_ex and r["n_new"] == n_new),
                        None,
                    )
                    for n_new in n_new_values
                ]
                xs = [x for x, y in zip(n_new_values, ys) if y is not None]
                ys = [y for y in ys if y is not None]
                if xs:
                    ax.plot(xs, ys, marker="o",
                            color=_N_EX_COLORS[ex_idx % len(_N_EX_COLORS)],
                            label=f"n_ex={n_ex}")
            ax.set_yscale("log")
            ax.set_title(f"{vname}\n({repo})", fontsize=8)
            ax.set_xlabel("n_new")
            ax.set_ylabel("wall_s (log)")
            ax.legend(fontsize=7)
    fig.suptitle("Scaling with n_new — one subplot per variant")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def _plot_lines_per_n_existing(results: list[dict], out: Path) -> None:  # pragma: no cover
    """Line chart: one subplot per (repo, n_existing), one line per variant, x = n_new."""
    if not _HAS_MATPLOTLIB:
        return
    repos = sorted({r["repo"] for r in results})
    n_new_values = sorted({r["n_new"] for r in results})
    cols = [(repo, n_ex) for repo in repos for n_ex in _n_ex_for_repo(results, repo)]
    fig, axes = plt.subplots(
        1, len(cols), figsize=(5 * len(cols), 4), sharey=False, squeeze=False
    )
    variant_colors = {v: _CHART_COLORS[i % len(_CHART_COLORS)]
                      for i, v in enumerate(_VARIANT_NAMES)}
    for col_idx, (repo, n_ex) in enumerate(cols):
        ax = axes[0][col_idx]
        for vname in _VARIANT_NAMES:
            ys = [
                next(
                    (r["wall_s"] for r in results
                     if r["variant"] == vname and r["repo"] == repo
                     and r["n_existing"] == n_ex and r["n_new"] == n_new),
                    None,
                )
                for n_new in n_new_values
            ]
            xs = [x for x, y in zip(n_new_values, ys) if y is not None]
            ys = [y for y in ys if y is not None]
            if xs:
                ax.plot(xs, ys, marker="o",
                        color=variant_colors[vname], label=vname)
        ax.set_yscale("log")
        ax.set_title(f"{repo}  n_ex={n_ex}")
        ax.set_xlabel("n_new")
        ax.set_ylabel("wall_s (log)")
        ax.legend(fontsize=7)
    fig.suptitle("Scaling with n_new — one subplot per n_existing")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def _plot_lines_all(results: list[dict], out: Path) -> None:  # pragma: no cover
    """Line chart: single plot, one line per (variant, n_existing) combination."""
    if not _HAS_MATPLOTLIB:
        return
    repos = sorted({r["repo"] for r in results})
    n_new_values = sorted({r["n_new"] for r in results})
    variant_markers = ["o", "s", "^", "D", "v", "P"]
    fig, axes = plt.subplots(
        1, len(repos), figsize=(8 * len(repos), 5), squeeze=False
    )
    for col_idx, repo in enumerate(repos):
        ax = axes[0][col_idx]
        n_ex_values = _n_ex_for_repo(results, repo)
        line_idx = 0
        for vname in _VARIANT_NAMES:
            v_idx = _VARIANT_NAMES.index(vname)
            for ex_idx, n_ex in enumerate(n_ex_values):
                ys = [
                    next(
                        (r["wall_s"] for r in results
                         if r["variant"] == vname and r["repo"] == repo
                         and r["n_existing"] == n_ex and r["n_new"] == n_new),
                        None,
                    )
                    for n_new in n_new_values
                ]
                xs = [x for x, y in zip(n_new_values, ys) if y is not None]
                ys = [y for y in ys if y is not None]
                if xs:
                    ax.plot(
                        xs, ys,
                        marker=variant_markers[v_idx % len(variant_markers)],
                        color=_N_EX_COLORS[ex_idx % len(_N_EX_COLORS)],
                        linestyle=["-", "--", ":", "-."][ex_idx % 4],
                        label=f"{vname} ex={n_ex}",
                    )
                line_idx += 1
        ax.set_yscale("log")
        ax.set_title(repo)
        ax.set_xlabel("n_new")
        ax.set_ylabel("wall_s (log)")
        ax.legend(fontsize=6, ncol=2)
    fig.suptitle("Scaling with n_new — all variants and n_existing")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


# ── Session fixture: generate charts after all tests finish ──────────────────


@pytest.fixture(scope="session", autouse=True)
def generate_benchmark_charts() -> Any:
    yield
    if not _RESULTS:
        return
    (RUN_DIR / "charts").mkdir(parents=True, exist_ok=True)
    with open(RUN_DIR / "results.json", "w") as fh:
        json.dump(_RESULTS, fh, indent=2)
    if _HAS_MATPLOTLIB:
        _plot_total_duration(_RESULTS, RUN_DIR / "charts" / "total_duration.png")
        _plot_per_profile(_RESULTS, RUN_DIR / "charts" / "per_profile.png")
        _plot_segments(_RESULTS, RUN_DIR / "charts" / "segments.png")
        _plot_retrieve(_RESULTS, RUN_DIR / "charts" / "retrieve.png")
        _plot_lines_per_variant(
            _RESULTS, RUN_DIR / "charts" / "lines_per_variant.png"
        )
        _plot_lines_per_n_existing(
            _RESULTS, RUN_DIR / "charts" / "lines_per_n_existing.png"
        )
        _plot_lines_all(_RESULTS, RUN_DIR / "charts" / "lines_all.png")


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
            # n_clusters derived per scale so stored pairs stay ~constant.
            n_clusters = max(1, n_ex // _CLUSTER_SIZE)
            locus_probs, cluster_refs = _init_profile_generator(N_LOCI, n_clusters)

            db = generate_scale_test_db(
                n_loci=N_LOCI,
                n_existing=n_ex,
                max_stored_distance=_MAX_STORED_DISTANCE,
                seed=n_ex,
                locus_probs=locus_probs,
                cluster_refs=cluster_refs,
            )
            dist_proto, allele_proto_id, locus_set_id, n_loci = _extract_protocol_info(db)

            type(self).base_dbs[n_ex] = db
            type(self).dist_protocols[n_ex] = dist_proto

            # Pre-generate new profiles for each n_new (deterministic seeds)
            for n_new in N_NEW:
                profs, samps = _make_realistic_profiles(
                    n_new,
                    allele_proto_id,
                    locus_set_id,
                    n_loci,
                    cluster_refs,
                    locus_probs,
                    seed=n_ex + n_new,
                )
                type(self).new_profiles[(n_ex, n_new)] = (profs, samps)

            # Base SQLite — versioned filename so parameter changes invalidate
            # old cached files automatically. Guard against partially-written
            # files: if the schema was created but the fill transaction was
            # never committed, the file has non-zero size but zero rows.
            sqlite_path = (
                BENCHMARK_DATA_DIR / f"bench_{_BENCH_VERSION}_base_{n_ex}.sqlite"
            )
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
                use_bulk_insert=variant["bulk"],
                use_int32_vocab=variant["int32_vocab"],
                use_flipped_loop=variant["flipped"],
            )

            profiler = pyinstrument.Profiler()
            profiler.start()
            try:
                t0 = perf_counter()
                env.app.handle(cmd)
                wall_s = perf_counter() - t0
            finally:
                profiler.stop()

            (RUN_DIR / "profiles").mkdir(parents=True, exist_ok=True)
            html_path = (
                RUN_DIR / "profiles"
                / f"{variant['name']}_{repo_type.value}_n{n_existing}_m{n_new}.html"
            )
            html_path.write_text(profiler.output_html())

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
                "rest_s": max(0.0, wall_s - sum(segments.values())),
            }
        )
        print(
            f"\n{variant['name']} {repo_type.value} ex={n_existing} n={n_new}: "
            f"{wall_s:.2f}s  ({wall_s / max(n_new, 1):.3f}s/profile)"
        )


# ── MSSQL variant (optional) ──────────────────────────────────────────────────

_MSSQL_PARAMS = [(v, n_new) for v in VARIANTS for n_new in N_NEW]
_MSSQL_IDS = [f"{v['name']}-mssql-n{n}" for v, n in _MSSQL_PARAMS]


def _wipe_seqdb_data(mssql_repo: Any, user_id: UUID, entities: list) -> None:
    """Delete all seqdb rows in FK-safe (reverse DAG) order.

    Called before reseeding with a different n_existing so that the DB is
    in a known-empty state for `fill_empty_sqlite_repository`.
    """
    with mssql_repo.uow() as uow:
        for entity in reversed(entities):
            mssql_repo.crud(
                uow, user_id, entity.model_class, CrudOperation.DELETE_ALL
            )


class _MssqlBenchmarkBase:
    """Shared setup/teardown and test body for MSSQL n_existing classes.

    Each concrete subclass sets `_N_EXISTING_MSSQL` and is collected as its
    own pytest class. Alphabetical ordering (1000 < 5000) ensures the smaller
    DB runs first; the larger class wipes and reseeds automatically when the
    existing profile count does not match.
    """

    entities: list
    dist_protocol: model.Protocol
    new_profiles: dict[tuple[str, int], tuple[list[model.SeqProfile], list[model.Sample]]]
    mssql_repo: Any
    base_db: dict

    _N_EXISTING_MSSQL: int  # set by subclasses

    @pytest.fixture(scope="class", autouse=True)
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

        n_clusters = max(1, n_ex // _CLUSTER_SIZE)
        locus_probs, cluster_refs = _init_profile_generator(N_LOCI, n_clusters)

        db = generate_scale_test_db(
            n_loci=N_LOCI,
            n_existing=n_ex,
            max_stored_distance=_MAX_STORED_DISTANCE,
            seed=n_ex,
            locus_probs=locus_probs,
            cluster_refs=cluster_refs,
        )
        dist_proto, allele_proto_id, locus_set_id, n_loci = _extract_protocol_info(db)
        type(self).base_db = db
        type(self).dist_protocol = dist_proto

        type(self).new_profiles = {}
        for v_idx, variant in enumerate(VARIANTS):
            for n_new in N_NEW:
                profs, samps = _make_realistic_profiles(
                    n_new,
                    allele_proto_id,
                    locus_set_id,
                    n_loci,
                    cluster_refs,
                    locus_probs,
                    seed=n_ex + n_new + v_idx * 10_000,
                )
                type(self).new_profiles[(variant["name"], n_new)] = (profs, samps)

        mssql_repo = create_mssql_repository(mssql_url, entities)
        current_count = count_seq_profiles(mssql_repo)
        if current_count != n_ex:
            if current_count > 0:
                _wipe_seqdb_data(mssql_repo, user_id, entities)
            dict_repo = create_dict_repository(
                pickle_file=None, db=db, entities=entities
            )
            fill_empty_sqlite_repository(dict_repo, mssql_repo, entities, user_id)
        type(self).mssql_repo = mssql_repo

    def _cleanup_variant_data(
        self,
        user_id: UUID,
        new_profs: list[model.SeqProfile],
        new_samps: list[model.Sample],
        is_pair: bool,
    ) -> None:
        """Delete any leftover rows for new_profs/new_samps (FK-safe order).

        For distances/pairs we must look up IDs first (no delete-by-FK API).
        Profile/sample existence is checked with EXISTS_SOME before deleting
        because DELETE_SOME raises InvalidIdsError for missing IDs.
        """
        new_prof_ids = [cast(UUID, p.id) for p in new_profs]
        new_samp_ids = [cast(UUID, s.id) for s in new_samps]
        new_prof_id_set = set(new_prof_ids)
        with self.mssql_repo.uow() as uow:
            if is_pair:
                all_pairs = self.mssql_repo.crud(
                    uow, user_id, model.SeqDistancePair,
                    CrudOperation.READ_ALL, return_copy=False,
                )
                pair_ids = [
                    cast(UUID, r.id) for r in all_pairs
                    if r.profile_id_a in new_prof_id_set
                    or r.profile_id_b in new_prof_id_set
                ]
                # DELETE_SOME uses IN() on the PK; pyodbc raises ODBC 07002
                # when a single query has >~2100 bound parameters, so delete
                # in chunks of _DELETE_CHUNK_SIZE to stay safely under that.
                for chunk in chunk_list(pair_ids, _DELETE_CHUNK_SIZE):
                    self.mssql_repo.crud(
                        uow, user_id, model.SeqDistancePair,
                        CrudOperation.DELETE_SOME, obj_ids=chunk,
                    )
            # Always delete SeqDistance rows: row-per-pair mode still writes
            # coverage-marker SeqDistance rows (content="{}") so that
            # get_profiles_without_seq_distance works correctly. These must be
            # removed before deleting profiles or the FK on seq_profile_id
            # raises a REFERENCE constraint violation (SQL Server error 547).
            all_dists = self.mssql_repo.crud(
                uow, user_id, model.SeqDistance,
                CrudOperation.READ_ALL, return_copy=False,
            )
            dist_ids = [
                cast(UUID, r.id) for r in all_dists
                if r.seq_profile_id in new_prof_id_set
            ]
            for chunk in chunk_list(dist_ids, _DELETE_CHUNK_SIZE):
                self.mssql_repo.crud(
                    uow, user_id, model.SeqDistance,
                    CrudOperation.DELETE_SOME, obj_ids=chunk,
                )
            existing_flags = self.mssql_repo.crud(
                uow, user_id, model.SeqProfile,
                CrudOperation.EXISTS_SOME, obj_ids=new_prof_ids,
            )
            existing_prof_ids = [
                pid for pid, ex in zip(new_prof_ids, existing_flags) if ex
            ]
            if existing_prof_ids:
                self.mssql_repo.crud(
                    uow, user_id, model.SeqProfile,
                    CrudOperation.DELETE_SOME, obj_ids=existing_prof_ids,
                )
            existing_samp_flags = self.mssql_repo.crud(
                uow, user_id, model.Sample,
                CrudOperation.EXISTS_SOME, obj_ids=new_samp_ids,
            )
            existing_samp_ids = [
                sid for sid, ex in zip(new_samp_ids, existing_samp_flags) if ex
            ]
            if existing_samp_ids:
                self.mssql_repo.crud(
                    uow, user_id, model.Sample,
                    CrudOperation.DELETE_SOME, obj_ids=existing_samp_ids,
                )

    @pytest.mark.parametrize("variant,n_new", _MSSQL_PARAMS, ids=_MSSQL_IDS)
    def test_variant(self, env: Env, variant: dict, n_new: int) -> None:
        n_ex = self._N_EXISTING_MSSQL
        new_profs, new_samps = self.new_profiles[(variant["name"], n_new)]
        user_id = env.get_root_user().id

        # Pre-cleanup: wipe any stale rows left by a previously interrupted run.
        self._cleanup_variant_data(user_id, new_profs, new_samps, variant["pair"])

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
                use_bulk_insert=variant["bulk"],
                use_int32_vocab=variant["int32_vocab"],
                use_flipped_loop=variant["flipped"],
            )

            profiler = pyinstrument.Profiler()
            profiler.start()
            try:
                t0 = perf_counter()
                env.app.handle(cmd)
                wall_s = perf_counter() - t0
            finally:
                profiler.stop()

            (RUN_DIR / "profiles").mkdir(parents=True, exist_ok=True)
            html_path = (
                RUN_DIR / "profiles"
                / f"{variant['name']}_SA_SQL_n{n_ex}_m{n_new}.html"
            )
            html_path.write_text(profiler.output_html())

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
            self._cleanup_variant_data(user_id, new_profs, new_samps, variant["pair"])

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
                "rest_s": max(0.0, wall_s - sum(segments.values())),
            }
        )
        print(
            f"\n{variant['name']} SA_SQL ex={n_ex} n={n_new}: "
            f"{wall_s:.2f}s  ({wall_s / max(n_new, 1):.3f}s/profile)"
        )


@pytest.mark.performance
@pytest.mark.mssql
class TestDistanceOptimizationBenchmarkMssql1000(_MssqlBenchmarkBase):
    """MSSQL benchmark at n_existing=1000.

    Runs before Mssql5000 (alphabetical order) so the DB is seeded small
    first; Mssql5000.setup wipes and reseeds to 5000 automatically.
    """

    _N_EXISTING_MSSQL = 1000


@pytest.mark.performance
@pytest.mark.mssql
class TestDistanceOptimizationBenchmarkMssql5000(_MssqlBenchmarkBase):
    """MSSQL benchmark at n_existing=5000."""

    _N_EXISTING_MSSQL = 5000


@pytest.mark.performance
@pytest.mark.mssql
class TestDistanceOptimizationBenchmarkMssql10000(_MssqlBenchmarkBase):
    """MSSQL benchmark at n_existing=10000."""

    _N_EXISTING_MSSQL = 10000
