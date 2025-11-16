"""
Unit test to detect unnecessarily long import statements that increase coupling.

This test creates a directed acyclic graph (DAG) of all imports within the gen-epix
package and identifies import statements that could be shortened without creating
circular imports.
"""

import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import pytest


@dataclass
class ModuleNode:
    """Represents a module in the import graph."""

    module_path: str
    file_path: str


@dataclass
class SymbolNode:
    """Represents a symbol (variable/class/function) in a module."""

    module_path: str
    file_path: str
    symbol_name: str


@dataclass
class ImportEdge:
    """Represents an import relationship in the graph."""

    source_module: str
    target_key: Union[str, tuple[str, str]]  # module_path or (module_path, symbol_name)
    line_number: int
    symbol_name: str | None
    is_original: bool
    is_current: bool
    file_path: str
    original_import_statement: str
    new_edge: tuple[str, int, str] | None = None


class ImportGraphAnalyzer:
    """Analyzes import relationships to find unnecessarily long imports."""

    def __init__(self):
        self.module_nodes: dict[str, ModuleNode] = {}
        self.symbol_nodes: dict[tuple[str, str], SymbolNode] = {}
        self.edges: list[ImportEdge] = []
        self.adjacency: dict[
            Union[str, tuple[str, str]], set[Union[str, tuple[str, str]]]
        ] = defaultdict(set)

    def add_module_node(self, module_path: str, file_path: str) -> None:
        """Add a module node to the graph."""
        if module_path not in self.module_nodes:
            self.module_nodes[module_path] = ModuleNode(module_path, file_path)

    def add_symbol_node(
        self, module_path: str, file_path: str, symbol_name: str
    ) -> None:
        """Add a symbol node to the graph."""
        key = (module_path, symbol_name)
        if key not in self.symbol_nodes:
            self.symbol_nodes[key] = SymbolNode(module_path, file_path, symbol_name)

    def add_import_edge(self, edge: ImportEdge) -> None:
        """Add an import edge to the graph."""
        self.edges.append(edge)
        source_key = edge.source_module
        self.adjacency[source_key].add(edge.target_key)

    def has_cycle(
        self,
        start_node: Union[str, tuple[str, str]],
        new_edge_target: Union[str, tuple[str, str]],
    ) -> bool:
        """Check if adding an edge would create a cycle."""
        # Simple DFS to check if new_edge_target can reach start_node
        visited = set()

        def dfs(node: Union[str, tuple[str, str]]) -> bool:
            if node == start_node:
                return True
            if node in visited:
                return False

            visited.add(node)

            # Check neighbors in current adjacency list
            for neighbor in self.adjacency.get(node, set()):
                if dfs(neighbor):
                    return True

            return False

        return dfs(new_edge_target)

    def find_shortest_paths(self) -> None:
        """Find shortest import paths and update edges accordingly."""
        # Create a mapping of what symbols are available from each module
        # via re-exports (e.g., gen_epix.commondb.api provides UpdateUserRequestBody)
        symbol_availability = defaultdict(set)  # module -> set of symbols available

        for edge in self.edges:
            if isinstance(edge.target_key, tuple):
                target_module, symbol_name = edge.target_key
                # Normalize the source module path - __init__ modules are accessible as their parent package
                source_module = edge.source_module
                if source_module.endswith(".__init__"):
                    source_module = source_module[:-9]  # Remove '.__init__'

                # The source module makes this symbol available
                symbol_availability[source_module].add((target_module, symbol_name))

        print(
            f"DEBUG: Symbol availability built for {len(symbol_availability)} modules"
        )

        # Check specific case
        test_symbol = ("gen_epix.commondb.api.organization", "UpdateUserRequestBody")
        modules_with_symbol = [
            module
            for module, symbols in symbol_availability.items()
            if test_symbol in symbols
        ]
        print(f"DEBUG: Modules that provide {test_symbol}: {modules_with_symbol}")

        # For each original import edge, see if we can find a shorter path
        original_edges = [e for e in self.edges if e.is_original and e.is_current]
        print(f"DEBUG: Processing {len(original_edges)} original edges")

        changes_made = 0

        for edge in original_edges:
            if not isinstance(edge.target_key, tuple):
                continue  # Skip module imports for now

            target_module, symbol_name = edge.target_key
            source_module = edge.source_module

            # Debug specific case
            if (
                symbol_name == "UpdateUserRequestBody"
                and target_module == "gen_epix.commondb.api.organization"
            ):
                print(
                    f"DEBUG: Processing UpdateUserRequestBody import from {source_module}"
                )

            # Look for modules that provide this symbol and are shorter paths
            best_intermediate = None
            best_length = len(target_module.split("."))

            for intermediate_module, symbols in symbol_availability.items():
                if (target_module, symbol_name) in symbols:
                    # This intermediate module provides the same symbol
                    intermediate_parts = intermediate_module.split(".")
                    target_parts = target_module.split(".")

                    if (
                        symbol_name == "UpdateUserRequestBody"
                        and target_module == "gen_epix.commondb.api.organization"
                    ):
                        print(f"  Considering intermediate: {intermediate_module}")
                        print(
                            f"    Intermediate parts: {len(intermediate_parts)}, Target parts: {len(target_parts)}"
                        )
                        print(
                            f"    Is prefix: {target_parts[:len(intermediate_parts)] == intermediate_parts}"
                        )
                        print(
                            f"    Would be shorter: {len(intermediate_parts) < len(target_parts)}"
                        )

                    # Check if it's genuinely shorter and a valid prefix
                    if (
                        len(intermediate_parts) < len(target_parts)
                        and len(intermediate_parts) < best_length
                        and target_parts[: len(intermediate_parts)]
                        == intermediate_parts
                    ):

                        # Check for cycles
                        if not self.has_cycle(source_module, intermediate_module):
                            best_intermediate = intermediate_module
                            best_length = len(intermediate_parts)

                            if symbol_name == "UpdateUserRequestBody":
                                print(
                                    f"    Found valid shorter path: {intermediate_module}"
                                )

            # Create shorter path if found
            if best_intermediate:
                # Create new edge
                new_edge = ImportEdge(
                    source_module=source_module,
                    target_key=(best_intermediate, symbol_name),
                    line_number=edge.line_number,
                    symbol_name=symbol_name,
                    is_original=False,
                    is_current=True,
                    file_path=edge.file_path,
                    original_import_statement=edge.original_import_statement,
                )

                # Update current edge
                edge.is_current = False
                edge.new_edge = (best_intermediate, new_edge.line_number, symbol_name)

                # Add the new edge
                self.add_import_edge(new_edge)
                changes_made += 1

                print(
                    f"DEBUG: Created shorter path: {source_module} -> {best_intermediate} for {symbol_name}"
                )

        print(f"DEBUG: Made {changes_made} changes")

    def _is_genuinely_shorter_path(
        self, source_module: str, intermediate_module: str, target_module: str
    ) -> bool:
        """Check if intermediate_module represents a genuinely shorter import path."""
        # Intermediate should be shorter than target
        target_parts = target_module.split(".")
        intermediate_parts = intermediate_module.split(".")

        # Intermediate should have fewer parts
        if len(intermediate_parts) >= len(target_parts):
            return False

        # Intermediate should be a prefix of target
        return target_parts[: len(intermediate_parts)] == intermediate_parts


class ImportStatementVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements from Python files."""

    def __init__(self, file_path: str, module_path: str):
        self.file_path = file_path
        self.module_path = module_path
        self.imports: list[tuple[int, str, str | None, str]] = (
            []
        )  # line, module, symbol, statement

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit 'from ... import ...' statements."""
        if node.module is None:
            return

        # Only process gen_epix imports
        if not node.module.startswith("gen_epix"):
            return

        line_no = node.lineno
        import_stmt = self._reconstruct_import_from(node)

        for alias in node.names:
            symbol_name = alias.name
            self.imports.append((line_no, node.module, symbol_name, import_stmt))

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Visit 'import ...' statements."""
        line_no = node.lineno

        for alias in node.names:
            if not alias.name.startswith("gen_epix"):
                continue

            import_stmt = f"import {alias.name}"
            if alias.asname:
                import_stmt += f" as {alias.asname}"

            self.imports.append((line_no, alias.name, None, import_stmt))

        self.generic_visit(node)

    def _reconstruct_import_from(self, node: ast.ImportFrom) -> str:
        """Reconstruct the 'from ... import ...' statement as a string."""
        module = node.module or ""
        names = []

        for alias in node.names:
            if alias.asname:
                names.append(f"{alias.name} as {alias.asname}")
            else:
                names.append(alias.name)

        return f"from {module} import {', '.join(names)}"


def scan_python_files(root_dir: Path) -> list[Path]:
    """Scan for all Python files in the gen_epix package."""
    python_files = []
    gen_epix_dir = root_dir / "gen_epix"

    if not gen_epix_dir.exists():
        return python_files

    ignore_patterns = {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
    }

    for py_file in gen_epix_dir.rglob("*.py"):
        # Skip files in ignored directories
        if any(ignore_pattern in str(py_file) for ignore_pattern in ignore_patterns):
            continue

        python_files.append(py_file)

    return python_files


def analyze_imports(project_root: Path) -> ImportGraphAnalyzer:
    """Analyze all imports in the gen_epix package and build the import graph."""
    analyzer = ImportGraphAnalyzer()
    python_files = scan_python_files(project_root)

    print(f"Analyzing imports in {len(python_files)} Python files...")

    # STAGE 1: Build the import graph
    for py_file in python_files:
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(py_file))

            # Convert file path to module path
            relative_path = py_file.relative_to(project_root)
            module_path = (
                str(relative_path.with_suffix("")).replace("\\", ".").replace("/", ".")
            )

            # Add module node
            analyzer.add_module_node(module_path, str(py_file))

            # Extract imports
            visitor = ImportStatementVisitor(str(py_file), module_path)
            visitor.visit(tree)

            # Add import edges
            for line_no, imported_module, symbol_name, import_stmt in visitor.imports:
                if symbol_name:
                    # Symbol import: module -> (imported_module, symbol)
                    target_key = (imported_module, symbol_name)
                    analyzer.add_symbol_node(imported_module, "", symbol_name)
                else:
                    # Module import: module -> imported_module
                    target_key = imported_module
                    analyzer.add_module_node(imported_module, "")

                edge = ImportEdge(
                    source_module=module_path,
                    target_key=target_key,
                    line_number=line_no,
                    symbol_name=symbol_name,
                    is_original=True,
                    is_current=True,
                    file_path=str(py_file),
                    original_import_statement=import_stmt,
                )
                analyzer.add_import_edge(edge)

        except (SyntaxError, UnicodeDecodeError, OSError) as e:
            print(f"Warning: Could not analyze {py_file}: {e}")

    # STAGE 2: Find shortest paths
    analyzer.find_shortest_paths()

    return analyzer


def test_shortest_import_path() -> None:
    """
    Test that all import statements use the shortest possible path without creating cycles.
    """
    # Get project root
    project_root = Path(__file__).parent.parent.parent.parent
    output_dir = project_root / "test" / "output"
    output_file = output_dir / "too_long_import_statements.tsv"

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    # Analyze imports
    analyzer = analyze_imports(project_root)

    # STAGE 3: Find updated edges (original imports that can be shortened)
    updated_edges = [e for e in analyzer.edges if e.is_original and not e.is_current]

    # Write results to tab-delimited file
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        f.write("location\tcurrent_import\tshortest_import\n")

        if not updated_edges:
            f.write("# No unnecessarily long import statements found!\n")
        else:
            for edge in updated_edges:
                location = f"{Path(edge.file_path).relative_to(project_root)}:{edge.line_number}"
                current_import = edge.original_import_statement

                # Generate shortest import from new_edge
                if edge.new_edge:
                    intermediate_module, _, symbol_name = edge.new_edge
                    if edge.symbol_name:
                        shortest_import = (
                            f"from {intermediate_module} import {edge.symbol_name}"
                        )
                    else:
                        shortest_import = f"import {intermediate_module}"
                else:
                    shortest_import = "ERROR: No new edge found"

                f.write(f"{location}\t{current_import}\t{shortest_import}\n")

    print(f"Results written to: {output_file}")

    # Print results to screen
    if updated_edges:
        print(f"\nFound {len(updated_edges)} unnecessarily long import statements:\n")
        print("LOCATION\t\t\t\tCURRENT IMPORT\t\t\t\tSUGGESTED IMPORT")
        print("=" * 120)

        for i, edge in enumerate(updated_edges[:20]):  # Show first 20
            location = (
                f"{Path(edge.file_path).relative_to(project_root)}:{edge.line_number}"
            )
            current_import = edge.original_import_statement

            if edge.new_edge:
                intermediate_module, _, _ = edge.new_edge
                if edge.symbol_name:
                    shortest_import = (
                        f"from {intermediate_module} import {edge.symbol_name}"
                    )
                else:
                    shortest_import = f"import {intermediate_module}"
            else:
                shortest_import = "ERROR"

            print(f"{location:<40}\t{current_import:<50}\t{shortest_import}")

        if len(updated_edges) > 20:
            print(
                f"\n... and {len(updated_edges) - 20} more (see {output_file} for complete list)"
            )
    else:
        print("\nNo unnecessarily long import statements found!")

    # Fail the test if any updated edges were found
    if updated_edges:
        failure_msg = (
            f"Found {len(updated_edges)} unnecessarily long import statements. "
            f"See {output_file} for complete list.\n\n"
            "First few examples:\n"
        )

        for i, edge in enumerate(updated_edges[:5]):
            location = (
                f"{Path(edge.file_path).relative_to(project_root)}:{edge.line_number}"
            )
            failure_msg += f"  {location} - {edge.original_import_statement}\n"

            if edge.new_edge:
                intermediate_module, _, _ = edge.new_edge
                if edge.symbol_name:
                    shortest_import = (
                        f"from {intermediate_module} import {edge.symbol_name}"
                    )
                else:
                    shortest_import = f"import {intermediate_module}"
                failure_msg += f"    Suggested: {shortest_import}\n"

        if len(updated_edges) > 5:
            failure_msg += f"  ... and {len(updated_edges) - 5} more\n"

        pytest.fail(failure_msg)


if __name__ == "__main__":
    # Allow running the test directly for debugging
    test_shortest_import_path()
