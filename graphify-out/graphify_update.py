#!/usr/bin/env python
"""Graphify incremental update script for gen-epix-api"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    # Step 2: Detect files
    print("Step 2: Detecting files...")
    try:
        from graphify.detect import detect

        result = detect(Path("."))
        Path("graphify-out/.graphify_detect.json").write_text(
            json.dumps(result, ensure_ascii=False), encoding="utf-8"
        )
        print(
            f"✓ Detected {result['total_files']} files · ~{result['total_words']} words"
        )
        print(f"  code: {len(result['files'].get('code', []))} files")
        print(f"  docs: {len(result['files'].get('document', []))} files")
    except Exception as e:
        print(f"✗ Detection failed: {e}")
        sys.exit(1)

    # Step 3A: AST extraction
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
            print("ℹ No code files to extract")
    except Exception as e:
        print(f"✗ AST extraction failed: {e}")
        sys.exit(1)

    # Step 3B: Semantic extraction (skip for code-only)
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
    print("ℹ Created empty semantic file (code-only corpus)")

    # Step 3C: Merge
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

        merged = {
            "nodes": merged_nodes,
            "edges": ast["edges"] + sem["edges"],
            "hyperedges": sem.get("hyperedges", []),
            "input_tokens": sem.get("input_tokens", 0),
            "output_tokens": sem.get("output_tokens", 0),
        }
        Path("graphify-out/.graphify_extract.json").write_text(
            json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"✓ Merged: {len(merged_nodes)} nodes, {len(merged['edges'])} edges")
    except Exception as e:
        print(f"✗ Merge failed: {e}")
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

        wrote = to_json(G, communities, "graphify-out/graph.json")
        if not wrote:
            print("⚠ Graph shrink-guard: existing graph has more nodes")
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
        from graphify.cli import _stamped_manifest_files
        from graphify.detect import save_manifest

        _corpus = detection.get("all_files") or detection["files"]
        _manifest_files = _stamped_manifest_files(_corpus, extraction, Path("."))
        _sem_types = ("document", "paper", "image")
        _dispatched = {
            f for t, fl in detection["files"].items() if t in _sem_types for f in fl
        }
        _stamped = {f for fl in _manifest_files.values() for f in fl}
        _cleared = _dispatched - _stamped
        _scan = {f for fl in _corpus.values() for f in fl}
        save_manifest(
            _manifest_files,
            root=".",
            scan_corpus=_scan,
            clear_semantic=_cleared or None,
        )

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
