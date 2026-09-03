---
name: write-docstring
description: "Write or improve Python docstrings and comments using this repository's Google-style conventions. Use for public APIs, modules, classes, functions, methods, Args, Returns, Yields, Raises, Attributes, overrides, and non-obvious implementation comments."
argument-hint: "Describe the Python code that needs a docstring."
---
# Write Python Docstrings

Use this skill when adding or improving docstrings and comments in Python code.
Follow the repository reference at
[docs/standards/google-python-style-guide-3.8-comments-and-docstrings.md](../../../docs/standards/google-python-style-guide-3.8-comments-and-docstrings.md)
for rules not covered here.

## Procedure

1. Inspect the target module, class, function, or method and its callers or base
   class when needed to determine the behavior.
2. If a docstring already exists, preserve it unless there is a concrete defect:
   an inaccuracy, a material omission, a required missing section for an explicit
   exception, a violated repository convention, or text made stale by the code.
   Detailed, accurate docstrings are authoritative documentation, not candidates
   for condensation. Do not replace them with a shorter paraphrase, discard
   caller-relevant lifecycle detail, or rewrite their structure merely to make
   wording more uniform. Make the smallest additive or corrective edit that
   addresses the identified defect, and retain useful examples, constraints,
   invariants, side effects, and nesting semantics already present.
3. When creating or updating docstrings, follow a bottom-up approach: start with
   the innermost functions and methods, then move to the containing classes,
   modules and packages. Make sure higher-level docstrings accurately summarize
   lower-level docstrings.
4. Always add a docstring to every module, class, function, method, nested
   function, private helper, property getter, static method, class method, and
   async function in scope. Visibility, nesting, decorators, and an inline
   `# type: ignore` on the signature never permit omitting a docstring. Use a
   one-line docstring only for a small, obvious, non-public helper. Public APIs,
   modules, packages, nontrivial code, and non-obvious behavior require a
   complete docstring. Do not skip docstrings that add no information, such as
   `"""Tests for foo.bar."""`, but keep them one line long. Test module
   docstrings must be created, but can be very brief. This rule does not apply
   to some specific cases that are documented further down in Step 10.
5. Describe what the code does and how callers should use it, not its internal
   implementation. Mention implementation details only when callers need to
   know them, such as whether an argument is mutated in place.
6. Write the docstring using triple double quotes. Keep every line at or under
   88 characters. Make the summary one physical sentence ending in `.`, `?`, or
   `!`. If the docstring has more content, put one blank line after the summary.
7. A complex or central method needs a complete docstring: a summary, caller-
   relevant lifecycle or side effects, and applicable `Args:`, `Returns:`,
   `Yields:`, and `Raises:` sections. Treat command dispatch, authorization,
   persistence, generated interfaces, stateful orchestration, and multi-branch
   workflows as complex. Do not narrate internal statements; explain phases,
   guarantees, mutations, and delegation that affect callers.
8. Any method that explicitly raises an exception must use a complete docstring.
   Describe relevant arguments and return values, and document each explicit,
   interface-relevant exception in `Raises:` with its triggering condition. Also
   document propagated exceptions when they are part of a public contract. Do
   not restate obvious types. Use a consistent hanging indent of two or four
   spaces within the file. This rule does not apply to some specific cases that
   are documented further down in Step 10.
9. For public classes with multiple responsibilities or lifecycle behavior, use
   a summary followed by paragraphs explaining their role, collaboration
   boundaries, lifecycle, side effects, and security or trust implications where
   relevant. Start the docstring with "Encapsulates...". Describe public attributes in
   an `Attributes:` section.
10. Rules for specific types of classes, overruling the behaviour above on specific
   aspects:
   a. Exception classes: describe what the error represents rather than when
      it is raised.
   b. Pydantic models (classes):
      i. Start the docstring with `Represents ...`.
      ii. Do not describe each field in an `Attributes:` section. Instead, make sure 
          that each field has an appropriate description. If field validators and/or
          serializers are used, document their purpose and behavior in the 
          corresponding `Field()` description, including normalization, accepted forms,
          derived values, and serialization behavior. Do not describe field validation 
          or serialization in the class docstring.
      iii. If model validators are used, document their purpose, invariants, and
          error conditions in a separate `Model validation:` paragraph in the class 
          description.
      iv. If model serializers are used, document their output representation, omitted 
          or derived values, and error conditions when applicable in a separate 
          `Model serialization:` paragraph. Decorated validator and serializer methods
          still need concise docstrings for coverage, but must not duplicate caller-
          facing contracts or include Google-style sections.
      v. Do not change a field default, declaration form, or runtime behavior solely to
         add a description; use the existing `Field()` or `Annotated` metadata pattern.
   c. FastAPI route handlers: including nested handlers, always require a
      docstring as their first statement. A router decorator's `description`
      parameter supplements OpenAPI documentation; it does not replace the
      Python docstring. A concise one-line docstring is sufficient when the
      decorator already supplies the complete caller-facing description.
   d. Programmatically overridden docstrings: if the body of the function, method,
      class or module contains a statement that assigns a value to __doc__
      (typically the first statement of the body), then there is technically no
      need for a docstring. However, for clarity and to avoid linting false 
      positives put in place the literal docstring
      `"""Docstring assigned automatically"""`.
11. Public module docstrings must state the module's responsibility and summarize
   its principal public types, functions, and collaboration boundary. Package
   docstrings in `__init__.py` must additionally summarize each group of
   imported or re-exported symbols. If an initializer executes statements other
   than imports, document their purpose in a separate paragraph.
12. Place a function, method, class, or module docstring as its first statement.
   In a function or method, it must appear immediately after the signature and
   before comments, nested definitions, or executable statements. Move
   explanatory comments below the docstring rather than placing a docstring
   after them.
13. For overridden methods, put a one-line docstring `See base method.` when behavior
   does not materially differ or there are no extra details, such as side effects.
   Otherwise put a full docstring.
14. Do not adjust inline comments. Do not update docstrings that are not within the
   requested scope.
15. Before finishing a module, make a coverage pass over every `def` and `async
   def`, including nested and underscore-prefixed definitions. Confirm each has
   a docstring immediately after its signature; comments, decorators, and
   type-checker directives do not count as documentation.

## Audit Script

Run the dependency-free AST audit after documentation changes:

```bash
python .agents/skills/write-docstring/scripts/check_docstrings.py <target>
```

Use `--only` after the target to select checks during focused work:

```bash
python .agents/skills/write-docstring/scripts/check_docstrings.py <target> \
      --only coverage pydantic raises
```

Available checks are:

- `coverage`: missing module, class, and function docstrings, excluding overload
   stubs.
- `exception-class`: exception classes with missing or potentially misleading
   descriptions.
- `pydantic`: Pydantic method contracts kept off validators and serializers, and
   required model-level validation or serialization documentation.
- `package`: non-blocking warnings for package docstrings that omit literal
   re-export names. Review them because a docstring may describe exports as a
   group.
- `raises`: direct exception paths missing applicable `Args:`, `Returns:`, or
   `Raises:` sections. It excludes Pydantic field/model validators and serializers
   and overload stubs.

The audit is structural. It cannot determine whether a description accurately
explains behavior, whether a field description fully covers decorator behavior,
or whether package export groups are meaningfully summarized. Review those
caller-facing contracts in the source before declaring the work complete.

After the audit, run the focused Ruff documentation check and the relevant
formatter and test commands for the changed scope. The audit complements these
checks; it does not replace them.

## Preferred Structure

```python
def divide(dividend: float, divisor: float) -> float:
    """Divide one number by another.

    Args:
        dividend: The number being divided.
        divisor: The number to divide by.

    Returns:
        The quotient.

    Raises:
        ZeroDivisionError: If `divisor` is zero.
    """
```

Keep types in annotations. Include them in the docstring only when a type's
meaning, constraints, units, shape, or accepted values need explanation.
