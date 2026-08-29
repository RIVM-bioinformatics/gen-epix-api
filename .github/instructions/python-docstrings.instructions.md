---
description: "Use when writing or reviewing docstrings and comments for new Python code (modules, classes, functions, methods). Covers when a docstring is required, summary-line format, Args/Returns/Raises sections, class/Attributes docs, overridden methods, and inline comments."
applyTo: "gen_epix/**/*.py,test/**/*.py,util/**/*.py,etl.py,run.py"
---
# Python Docstrings & Comments

Full reference:
[docs/standards/google-python-style-guide-3.8-comments-and-docstrings.md](../../docs/standards/google-python-style-guide-3.8-comments-and-docstrings.md)
(Google Python Style Guide §3.8). Follow it for anything not covered below.

## Most important rules

1. **When a docstring is required**: public API, nontrivial size, or
   non-obvious logic. Skip docstrings that add no information (e.g.
   `"""Tests for foo.bar."""`). Test module docstrings are optional — add one
   only when there's setup/environment info a reader needs.
2. **Format**: triple double quotes (`"""`). Summary line is one physical
   sentence ending in `.`, `?`, or `!`. If more follows, leave one blank line,
   then continue at the same indent as the opening quotes. Keep lines at or
   under 88 characters (89 for Claude-specific work) per this repo's standard
   — the source guide's 80-character example is superseded by that limit.
3. **Say what, not how**: describe calling syntax and semantics — enough to
   call the function without reading its body. Only mention implementation
   details the caller needs to know (e.g. "mutates `items` in place").
4. **Args/Returns/Yields/Raises**: use these sections only when they add
   meaning beyond the type hints already in the signature. Don't restate
   obvious types. Use a consistent hanging indent (2 or 4 spaces) within a
   file. `Raises:` lists only exceptions relevant to the interface, not ones
   caused by violating the documented API.
5. **Classes**: one-line summary describing what an instance *represents*,
   not "Class that...". Exceptions describe what the error *represents*
   ("No more cheese is available."), not when it's raised. Document public
   attributes in an `Attributes:` section using the same style as `Args:`.
6. **Overridden methods**: decorate with `@override` and omit the docstring
   if behavior matches the base method. Add a docstring only when behavior
   materially differs or extra details (e.g. side effects) matter.
7. **Comments**: explain the non-obvious "why", never restate what the next
   line already shows. At least 2 spaces before `#`, at least 1 space after.
   Write complete, well-punctuated sentences.
