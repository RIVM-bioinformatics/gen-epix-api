from __future__ import annotations

import argparse
import inspect
from pathlib import Path

TARGET_OLD = 'MutantDict = Annotated[dict[str, Callable], "Mutant"]'
TARGET_NEW = 'MutantDict = Annotated[Dict[str, Callable], "Mutant"]'
DICT_IMPORT = "from typing import Dict"
IMPORT_ANCHOR = "from typing import ClassVar\n"


def find_template_file() -> Path:
    try:
        import mutmut.trampoline_templates as templates
    except Exception as exc:
        raise SystemExit(
            "Could not import mutmut.trampoline_templates. "
            "Activate your mutation virtual environment and install "
            "requirements-mutation.txt first."
        ) from exc

    return Path(inspect.getfile(templates)).resolve()


def patch_template_text(text: str) -> tuple[str, bool]:
    already_patched = TARGET_NEW in text and DICT_IMPORT in text
    if already_patched:
        return text, False

    if TARGET_OLD not in text:
        raise SystemExit(
            "Could not find expected mutmut template alias line to patch. "
            "Template format may have changed."
        )

    updated = text
    if DICT_IMPORT not in updated:
        if IMPORT_ANCHOR not in updated:
            raise SystemExit(
                "Could not find import anchor line in mutmut template. "
                "Template format may have changed."
            )
        updated = updated.replace(IMPORT_ANCHOR, IMPORT_ANCHOR + DICT_IMPORT + "\n", 1)

    updated = updated.replace(TARGET_OLD, TARGET_NEW, 1)
    return updated, True


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Patch installed mutmut trampoline template to avoid "
            "module-name collisions with bare dict type aliasing."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check status. Exit 0 when patched, 1 when patch is needed.",
    )
    args = parser.parse_args()

    template_path = find_template_file()
    original = template_path.read_text(encoding="utf-8")
    patched, changed = patch_template_text(original)

    if args.check:
        if changed:
            print(f"Patch needed: {template_path}")
            raise SystemExit(1)
        print(f"Patch already applied: {template_path}")
        return

    if changed:
        template_path.write_text(patched, encoding="utf-8")
        print(f"Patched mutmut template: {template_path}")
    else:
        print(f"Mutmut template already patched: {template_path}")


if __name__ == "__main__":
    main()
