"""
Mermaid-based ERM diagram generator.

Produces Mermaid ``erDiagram`` markdown files from domain model definitions.

Two versions per diagram:
  - **Detailed**: entity blocks include all field properties (PK/FK/type annotations)
  - **Simplified**: entity names and relationship lines only (no properties)

Usage:
    python -m docs.erm.erm_mermaid               # writes to docs/erm/
    python -m docs.erm.erm_mermaid --dir /tmp/out # writes to custom dir
"""

from __future__ import annotations

import argparse
import re
import types
import typing
from pathlib import Path
from typing import get_args, get_origin
from uuid import UUID

from pydantic import BaseModel

from docs.erm.erm import ErmGenerator
from gen_epix.fastapp import Domain
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import FieldType

# ---------------------------------------------------------------------------
# Type-annotation helpers
# ---------------------------------------------------------------------------

_SIMPLE_TYPE_MAP: dict[type, str] = {
    str: "string",
    int: "int",
    float: "float",
    bool: "bool",
    bytes: "bytes",
    UUID: "UUID",
}


def _annotation_to_mermaid_type(annotation: type | None) -> str:
    """
    Convert a Python / Pydantic type annotation to a short Mermaid-friendly
    type string.  Handles Optional, Union, list, set, dict, Enum, etc.
    """
    if annotation is None:
        return "any"

    # Unwrap Optional / Union with None  (e.g. ``str | None``)
    origin = get_origin(annotation)
    if origin is types.UnionType or origin is typing.Union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            return _annotation_to_mermaid_type(args[0])
        return " | ".join(_annotation_to_mermaid_type(a) for a in args)

    # list[X], set[X], frozenset[X], etc.
    if origin in (list, set, frozenset, tuple):
        inner_args = get_args(annotation)
        container = origin.__name__
        if inner_args:
            inner = ", ".join(_annotation_to_mermaid_type(a) for a in inner_args)
            return f"{container}[{inner}]"
        return container

    # dict[K, V]
    if origin is dict:
        k_args = get_args(annotation)
        if k_args and len(k_args) == 2:
            return f"dict[{_annotation_to_mermaid_type(k_args[0])}, {_annotation_to_mermaid_type(k_args[1])}]"
        return "dict"

    # Simple well-known types
    if annotation in _SIMPLE_TYPE_MAP:
        return _SIMPLE_TYPE_MAP[annotation]

    # Enum sub-classes
    import enum

    if isinstance(annotation, type) and issubclass(annotation, enum.Enum):
        return "enum"

    # datetime types
    import datetime as _dt

    _DT_NAMES = {_dt.datetime: "timestamp", _dt.date: "date", _dt.time: "time"}
    if annotation in _DT_NAMES:
        return _DT_NAMES[annotation]

    # Pydantic / domain model references → just the class name
    if isinstance(annotation, type):
        return annotation.__name__

    # Fallback
    return re.sub(r"[<>]", "", str(annotation))


# ---------------------------------------------------------------------------
# Per-entity rendering
# ---------------------------------------------------------------------------


def _field_marker(field_type: FieldType) -> str:
    """Return Mermaid column marker (PK / FK) or empty string."""
    if field_type is FieldType.ID:
        return "PK"
    if field_type is FieldType.LINK:
        return "FK"
    return ""


def _render_entity_block(model_class: type[BaseModel], entity: Entity) -> list[str]:
    """
    Return the Mermaid lines for a single entity block **with** attributes.
    Example output::

        Sample {
            UUID id PK
            string code
            UUID data_collection_id FK
        }
    """
    lines: list[str] = []
    lines.append(f"    {model_class.__name__} {{")

    # Combine model_fields and model_computed_fields
    all_fields: dict = dict(model_class.model_fields)
    all_fields.update(model_class.model_computed_fields)

    for field_name, field_meta in entity._fields.items():
        ft: FieldType = field_meta["type"]

        # Skip RELATIONSHIP fields (they are the object-side of a link, not
        # persisted columns)
        if ft is FieldType.RELATIONSHIP:
            continue

        # Resolve annotation
        pydantic_field = all_fields.get(field_name)
        if pydantic_field is not None:
            ann = getattr(pydantic_field, "annotation", None)
        else:
            ann = None

        type_str = _annotation_to_mermaid_type(ann)
        marker = _field_marker(ft)
        if marker:
            lines.append(f"        {type_str} {field_name} {marker}")
        else:
            lines.append(f"        {type_str} {field_name}")

    lines.append("    }")
    return lines


# ---------------------------------------------------------------------------
# Relationship rendering
# ---------------------------------------------------------------------------


def _render_relationships(
    model_classes: list[type[BaseModel]],
) -> list[str]:
    """
    Generate Mermaid relationship lines for a set of model classes.

    Each Link in an entity defines a many-to-one relationship:
        SourceEntity }o--|| TargetEntity : "fk_field"

    We only emit a relationship when both sides are in *model_classes* so that
    diagrams scoped to a service type are self-contained.
    """
    class_names = {x.__name__ for x in model_classes}
    lines: list[str] = []
    seen: set[tuple[str, str, str]] = set()

    for model_class in model_classes:
        entity: Entity | None = getattr(model_class, "ENTITY", None)
        if entity is None or not entity.links:
            continue
        source = model_class.__name__
        for link in entity.links.values():
            target = link.link_model_class.__name__
            if target not in class_names:
                continue
            fk = link.link_field_name
            key = (source, target, fk)
            if key in seen:
                continue
            seen.add(key)
            # Many-to-one: source has FK → target is the "one" side
            lines.append(f'    {source} }}o--|| {target} : "{fk}"')

    return lines


# ---------------------------------------------------------------------------
# Diagram assembly
# ---------------------------------------------------------------------------


def _build_diagram(
    model_classes: list[type[BaseModel]],
    *,
    detailed: bool,
    title_comment: str = "",
) -> str:
    """
    Build a complete Mermaid erDiagram string.

    Parameters
    ----------
    model_classes
        Ordered list of model classes to include.
    detailed
        If True, include entity attribute blocks.
    title_comment
        Optional comment line placed at the top of the diagram.
    """
    parts: list[str] = []
    parts.append("```mermaid")
    parts.append("erDiagram")

    if title_comment:
        parts.append(f"    %% {title_comment}")
        parts.append("")

    # Relationships first (easier to read in Mermaid)
    rel_lines = _render_relationships(model_classes)
    if rel_lines:
        parts.append("    %% Relationships")
        parts.extend(rel_lines)
        parts.append("")

    if detailed:
        parts.append("    %% Entity definitions")
        for model_class in model_classes:
            entity: Entity | None = getattr(model_class, "ENTITY", None)
            if entity is None:
                continue
            parts.extend(_render_entity_block(model_class, entity))
            parts.append("")
    else:
        # In simplified mode, entities without any links (neither as source nor
        # target) would be invisible.  Add them as empty blocks so they show up.
        mentioned = set()
        for line in rel_lines:
            # Extract entity names from relationship lines
            for token in line.split():
                if token[0].isupper():
                    mentioned.add(token)
        for model_class in model_classes:
            if model_class.__name__ not in mentioned:
                parts.append(f"    {model_class.__name__} {{")
                parts.append("    }")
                parts.append("")

    parts.append("```")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# File writer helper
# ---------------------------------------------------------------------------


def _write_md(path: Path, title: str, description: str, diagram: str) -> None:
    """Write a Markdown file wrapping a Mermaid diagram."""
    content = f"# {title}\n\n{description}\n\n{diagram}\n"
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# MermaidErmGenerator
# ---------------------------------------------------------------------------


class MermaidErmGenerator(ErmGenerator):
    """
    Generates Mermaid ``erDiagram`` markdown files from domain model
    definitions.

    For each domain (and each service type within a domain) two files are
    produced:

    - **detailed** — entities with field properties, PK/FK markers, types
    - **simplified** — entity names and relationship lines only
    """

    def generate_erm_diagrams(self, dir: Path) -> None:
        """Generate Mermaid ERD markdown files into *dir*."""
        dir = Path(dir)
        dir.mkdir(parents=True, exist_ok=True)

        print(f"Generating Mermaid ERDs in {dir}")
        for domain in self.domains:
            print(f"\n=== {domain.name} ===")
            self._generate_for_domain(domain, dir)
            self._generate_for_service(domain, dir)
        print("\nDone.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_for_domain(domain: Domain, dir: Path) -> None:
        sorted_models = domain.get_dag_sorted_models(persistable=True)
        domain_lower = domain.name.lower()

        # Detailed
        diagram_detailed = _build_diagram(
            sorted_models,
            detailed=True,
            title_comment=f"{domain.name} — all persistable entities (detailed)",
        )
        _write_md(
            dir / f"{domain_lower}.detailed.md",
            title=f"{domain.name} — Detailed Entity-Relationship Diagram",
            description=(
                f"Auto-generated from domain model definitions.  "
                f"Contains **{len(sorted_models)}** persistable entities with their "
                f"field definitions."
            ),
            diagram=diagram_detailed,
        )

        # Simplified
        diagram_simple = _build_diagram(
            sorted_models,
            detailed=False,
            title_comment=f"{domain.name} — all persistable entities (simplified)",
        )
        _write_md(
            dir / f"{domain_lower}.md",
            title=f"{domain.name} — Simplified Entity-Relationship Diagram",
            description=(
                f"Auto-generated from domain model definitions.  "
                f"Contains **{len(sorted_models)}** persistable entities — "
                f"relationships only, no field details."
            ),
            diagram=diagram_simple,
        )

    @staticmethod
    def _generate_for_service(domain: Domain, dir: Path) -> None:
        domain_lower = domain.name.lower()
        for service_type in sorted(domain.get_service_types(), key=lambda s: s.value):
            model_classes = list(domain.get_models_for_service_type(service_type))
            if not model_classes:
                continue
            svc_lower = service_type.value.lower()
            tag = f"{domain_lower}.{svc_lower}"

            # Detailed
            diagram_detailed = _build_diagram(
                model_classes,
                detailed=True,
                title_comment=f"{domain.name} / {service_type.value} (detailed)",
            )
            _write_md(
                dir / f"{tag}.detailed.md",
                title=f"{domain.name} / {service_type.value} — Detailed ERD",
                description=(
                    f"Auto-generated.  Service type **{service_type.value}** "
                    f"— {len(model_classes)} entities."
                ),
                diagram=diagram_detailed,
            )

            # Simplified
            diagram_simple = _build_diagram(
                model_classes,
                detailed=False,
                title_comment=f"{domain.name} / {service_type.value} (simplified)",
            )
            _write_md(
                dir / f"{tag}.md",
                title=f"{domain.name} / {service_type.value} — Simplified ERD",
                description=(
                    f"Auto-generated.  Service type **{service_type.value}** "
                    f"— {len(model_classes)} entities, relationships only."
                ),
                diagram=diagram_simple,
            )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Mermaid ER diagrams from Gen-EpiX domain models."
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Output directory (default: same directory as this script)",
    )
    args = parser.parse_args()
    out = args.dir if args.dir is not None else Path(__file__).parent
    MermaidErmGenerator().generate_erm_diagrams(out)
