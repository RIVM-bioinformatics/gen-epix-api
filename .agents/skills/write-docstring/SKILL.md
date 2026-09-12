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
4. Add docstrings to production modules and classes. Add function and method
   docstrings when they are public, nontrivial, or non-obvious. Private helpers
   and nested functions need docstrings only when their size or behavior meets
   those function criteria. Test-module docstrings are optional and should be
   added only when they explain unusual setup, execution, or environment
   requirements; do not add placeholders such as `"""Tests for foo.bar."""`.
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
8. Document exceptions in `Raises:` when they are relevant to the caller-facing
   contract, including propagated exceptions when applicable. Do not document
   exceptions raised only because a caller violated the documented API. Include
   `Args:`, `Returns:`, and `Yields:` only when they add meaning beyond names and
   annotations. Use a consistent hanging indent of two or four spaces.
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
      i. Start the docstring with `Represents`. If the model is a subclass of `Command`,
         i.e. representing an action, start the docstring with
         `Represents a request to execute`.
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
          `Model serialization:` paragraph. Add concise method docstrings to
          decorated validators and serializers when their implementation is
          nontrivial or non-obvious, but do not duplicate caller-facing contracts
          or include Google-style sections.
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
13. An `@override` method does not need a redundant docstring when it preserves
   the base contract. Document material contract differences and added side
   effects. Without `@override`, provide the docstring required by the standard.
14. Do not adjust inline comments. Do not update docstrings that are not within the
   requested scope.
15. Before finishing, review public, nontrivial, and non-obvious definitions in
   scope for accurate docstrings. Comments, decorators other than `@override`,
   and type-checker directives do not count as documentation.

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

- `coverage`: missing production-module and class docstrings, plus missing
   docstrings on structurally public top-level functions and public methods. It
   checks private and nested classes, but excludes repository test modules,
   overloads, `@override` methods, private functions, and nested functions;
   review nontrivial or non-obvious excluded functions manually.
- `exception-class`: exception classes with missing or potentially misleading
   descriptions.
- `pydantic`: Pydantic method contracts kept off validators and serializers, and
   required model-level validation or serialization documentation.
- `package`: non-blocking warnings for package docstrings that omit literal
   re-export names. Review them because a docstring may describe exports as a
   group.
- `raises`: non-blocking prompts to review public direct exception paths that
   lack `Raises:`. It excludes overrides, Pydantic validators and serializers,
   overloads, and private helpers; decide manually whether an exception is part
   of the caller-facing contract.

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
