#!/usr/bin/env python
"""Graphify incremental update script for gen-epix-api"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    # Step 2: Detect changed files (incremental, diffed against graphify-out/manifest.json)
    print("Step 2: Detecting changed files...")
    try:
        from graphify.detect import detect_incremental

        incremental = detect_incremental(Path("."))
        Path("graphify-out/.graphify_incremental.json").write_text(
            json.dumps(incremental, ensure_ascii=False), encoding="utf-8"
        )
        new_total = incremental.get("new_total", 0)
        deleted = list(incremental.get("deleted_files", []))
        if new_total == 0 and not deleted:
            print("No files changed since last run. Nothing to update.")
            return
        if deleted:
            print(f"  {len(deleted)} deleted file(s) to prune.")
        if new_total:
            print(f"  {new_total} new/changed file(s) to re-extract.")

        result = {
            "files": incremental.get("new_files", {}),
            "all_files": incremental.get("files", {}),
            "total_files": new_total,
            "total_words": incremental.get("total_words", 0),
            "skipped_sensitive": incremental.get("skipped_sensitive", []),
            "needs_graph": True,
        }
        Path("graphify-out/.graphify_detect.json").write_text(
            json.dumps(result, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as e:
        print(f"✗ Detection failed: {e}")
        sys.exit(1)

    # Step 3A: AST extraction (only the new/changed code files)
    print("\nStep 3A: Extracting code structure (AST)...")
    try:
        from graphify.extract import collect_files, extract

        code_files = []
        for f in result.get("files", {}).get("code", []):
            code_files.extend(collect_files(Path(f)) if Path(f).is_dir() else [Path(f)])

        if code_files:
            ast_result = extract(code_files, cache_root=Path("."))
            Path("graphify-out/.graphify_ast.json").write_text(
                json.dumps(ast_result, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            print(
                f"✓ AST: {len(ast_result['nodes'])} nodes, {len(ast_result['edges'])} edges"
            )
        else:
            Path("graphify-out/.graphify_ast.json").write_text(
                json.dumps(
                    {"nodes": [], "edges": [], "input_tokens": 0, "output_tokens": 0},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            print("ℹ No changed code files to extract")
    except Exception as e:
        print(f"✗ AST extraction failed: {e}")
        sys.exit(1)

    # Step 3B: Semantic extraction (skipped - CI has no LLM backend for docs/papers/images)
    print("\nStep 3B: Preparing semantic extraction...")
    Path("graphify-out/.graphify_semantic.json").write_text(
        json.dumps(
            {
                "nodes": [],
                "edges": [],
                "hyperedges": [],
                "input_tokens": 0,
                "output_tokens": 0,
            }
        ),
        encoding="utf-8",
    )
    print("ℹ Created empty semantic file (CI is code-only, no LLM backend)")

    # Step 3C: Merge AST + semantic delta
    print("\nStep 3C: Merging AST + semantic...")
    try:
        ast = json.loads(
            Path("graphify-out/.graphify_ast.json").read_text(encoding="utf-8")
        )
        sem = json.loads(
            Path("graphify-out/.graphify_semantic.json").read_text(encoding="utf-8")
        )

        seen = {n["id"] for n in ast["nodes"]}
        merged_nodes = list(ast["nodes"])
        for n in sem["nodes"]:
            if n["id"] not in seen:
                merged_nodes.append(n)
                seen.add(n["id"])

        new_extraction = {
            "nodes": merged_nodes,
            "edges": ast["edges"] + sem["edges"],
            "hyperedges": sem.get("hyperedges", []),
            "input_tokens": sem.get("input_tokens", 0),
            "output_tokens": sem.get("output_tokens", 0),
        }
        Path("graphify-out/.graphify_extract.json").write_text(
            json.dumps(new_extraction, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(
            f"✓ Merged: {len(merged_nodes)} nodes, {len(new_extraction['edges'])} edges"
        )
    except Exception as e:
        print(f"✗ Merge failed: {e}")
        sys.exit(1)

    # Step 3D: Fold this run's delta into the existing graph.json. Using
    # build_merge (instead of rebuilding from scratch) preserves nodes for
    # files this code-only CI run never touches - e.g. doc/semantic nodes
    # from a prior full local `/graphify` build - and only replaces nodes for
    # files actually re-extracted this run, pruning only genuinely deleted
    # files. A from-scratch rebuild here is what previously tripped the
    # graph.json shrink-guard: it discarded everything not in this run's
    # code-only extraction.
    print("\nStep 3D: Merging into existing graph...")
    try:
        from graphify.build import build_merge
        from graphify.cli import _stamped_manifest_files
        from graphify.detect import save_manifest

        # Measure how much of a shrink genuine deletions can account for, before
        # the merge: nodes in the current graph whose source file is no longer in
        # the repo. Step 4 uses this as the ceiling on an allowed shrink.
        existing_path = Path("graphify-out/graph.json")
        existing_nodes = (
            json.loads(existing_path.read_text(encoding="utf-8")).get("nodes", [])
            if existing_path.exists()
            else []
        )
        existing_count = len(existing_nodes)
        orphaned_count = 0
        for n in existing_nodes:
            sf = n.get("source_file")
            if sf and not Path(sf).exists():
                orphaned_count += 1
        if orphaned_count:
            print(
                f"  {orphaned_count} node(s) in the current graph belong to files "
                f"no longer in the repo"
            )

        prune = deleted or None
        G = build_merge(
            [new_extraction],
            graph_path="graphify-out/graph.json",
            prune_sources=prune,
            root=".",
            directed=False,
        )
        merged_out = {
            "nodes": [{"id": n, **d} for n, d in G.nodes(data=True)],
            "edges": [
                {
                    **{
                        k: val
                        for k, val in d.items()
                        if k not in ("_src", "_tgt", "source", "target")
                    },
                    "source": d.get("_src", u),
                    "target": d.get("_tgt", v),
                }
                for u, v, d in G.edges(data=True)
            ],
            "hyperedges": list(G.graph.get("hyperedges", [])),
            "input_tokens": new_extraction.get("input_tokens", 0),
            "output_tokens": new_extraction.get("output_tokens", 0),
        }
        Path("graphify-out/.graphify_extract.json").write_text(
            json.dumps(merged_out, ensure_ascii=False), encoding="utf-8"
        )
        print(
            f"✓ Merged with existing graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges"
        )

        # Stamp the manifest against this run's delta only, so the next
        # --update diffs against today's state instead of re-queueing
        # everything or masking a failed chunk.
        _manifest_files = _stamped_manifest_files(
            incremental["files"], new_extraction, Path(".")
        )
        _sem_types = ("document", "paper", "image")
        _dispatched = {
            f
            for t, fl in incremental.get("new_files", {}).items()
            if t in _sem_types
            for f in fl
        }
        _stamped = {f for fl in _manifest_files.values() for f in fl}
        _cleared = _dispatched - _stamped
        _scan = {f for fl in incremental["files"].values() for f in fl}
        save_manifest(
            _manifest_files, root=".", scan_corpus=_scan, clear_semantic=_cleared or None
        )
        print("✓ Manifest saved")
    except Exception as e:
        print(f"✗ Graph merge failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Step 4: Build graph, cluster, analyze
    print("\nStep 4: Building graph and clustering...")
    try:
        from graphify.analyze import (
            god_nodes,
            suggest_questions,
            surprising_connections,
        )
        from graphify.build import build_from_json
        from graphify.cluster import cluster, score_all
        from graphify.export import to_json
        from graphify.report import generate

        extraction = json.loads(
            Path("graphify-out/.graphify_extract.json").read_text(encoding="utf-8")
        )
        detection = json.loads(
            Path("graphify-out/.graphify_detect.json").read_text(encoding="utf-8")
        )

        G = build_from_json(extraction, root=".", directed=False)

        if G.number_of_nodes() == 0:
            print("✗ Graph is empty - extraction produced no nodes")
            sys.exit(1)

        communities = cluster(G)
        cohesion = score_all(G, communities)
        gods = god_nodes(G)
        surprises = surprising_connections(G, communities)

        labels = {cid: f"Community {cid}" for cid in communities}
        questions = suggest_questions(G, communities, labels)

        # to_json refuses any net node loss. After an incremental merge a loss is
        # expected when files were deleted, so allow a shrink up to what the
        # deleted files account for and fail on anything beyond it - an
        # unexplained loss means missing chunks or a fuzzy-dedup collapse.
        deficit = existing_count - G.number_of_nodes()
        force = False
        if deficit > 0:
            if deficit <= orphaned_count:
                force = True
                print(
                    f"ℹ Net -{deficit} node(s), within the {orphaned_count} node(s) "
                    f"whose source files were deleted from the repo - writing."
                )
            else:
                print(
                    f"✗ Graph shrink-guard: net -{deficit} node(s), but only "
                    f"{orphaned_count} are explained by deleted files."
                )
                print(
                    "  The unexplained loss points at missing chunks or a fuzzy-dedup "
                    "collapse. Investigate before forcing."
                )
                sys.exit(1)

        wrote = to_json(G, communities, "graphify-out/graph.json", force=force)
        if not wrote:
            print("⚠ Graph export refused the write (see warning above)")
            sys.exit(1)

        report = generate(
            G,
            communities,
            cohesion,
            labels,
            gods,
            surprises,
            detection,
            {"input": 0, "output": 0},
            ".",
            suggested_questions=questions,
        )
        Path("graphify-out/GRAPH_REPORT.md").write_text(report, encoding="utf-8")

        analysis = {
            "communities": {str(k): v for k, v in communities.items()},
            "cohesion": {str(k): v for k, v in cohesion.items()},
            "gods": gods,
            "surprises": surprises,
            "questions": questions,
        }
        Path("graphify-out/.graphify_analysis.json").write_text(
            json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(
            f"✓ Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities"
        )
    except Exception as e:
        print(f"✗ Build failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Step 9: Save manifest and report
    print("\nStep 9: Finalizing...")
    try:
        # Update cost tracker
        cost_path = Path("graphify-out/cost.json")
        if cost_path.exists():
            cost = json.loads(cost_path.read_text(encoding="utf-8"))
        else:
            cost = {"runs": [], "total_input_tokens": 0, "total_output_tokens": 0}

        cost["runs"].append(
            {
                "date": datetime.now(timezone.utc).isoformat(),
                "input_tokens": 0,
                "output_tokens": 0,
                "files": detection.get("total_files", 0),
            }
        )
        cost_path.write_text(
            json.dumps(cost, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Cleanup
        import glob

        for f in glob.glob("graphify-out/.graphify_*.json"):
            if Path(f).name not in [
                ".graphify_analysis.json",
                ".graphify_python",
                ".graphify_root",
                ".graphify_labels.json",
            ]:
                Path(f).unlink(missing_ok=True)

        print(f"✓ Manifest saved, cost tracker updated")
        print("\n" + "=" * 60)
        print("Graph complete. Outputs in graphify-out/")
        print("  graph.html            - interactive graph, open in browser")
        print("  GRAPH_REPORT.md       - audit report")
        print("  graph.json            - raw graph data")
        print("=" * 60)
    except Exception as e:
        print(f"✗ Finalization failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    print("\n✓ Update complete!")


if __name__ == "__main__":
    main()
