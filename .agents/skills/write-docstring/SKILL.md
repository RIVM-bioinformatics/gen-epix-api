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
2. If a docstring already exists, evaluate whether it accurately and completely
   describes the code. Update it as necessary as described further down. However,
   do not adjust a large docstring unnecessarily since it may have been put up 
   manually; focus on accuracy and completeness.
3. When creating or updating docstrings, follow a bottom-up approach: start with
   the innermost functions and methods, then move to the containing classes, 
   modules and packages. Make sure higher-level docstrings accurately summarize
   lower-level docstrings.
4. Always add a docstring. Use a one-line docstring only for a small, obvious,
   non-public helper. Public APIs, modules, packages, nontrivial code, and
   non-obvious behavior require a complete docstring. Do not skip docstrings
   that add no information, such as `"""Tests for foo.bar."""`, but keep them one
   line long. Test module docstrings must be created, but can be very brief.
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
   spaces within the file.
9. For public classes with multiple responsibilities or lifecycle behavior, use
   a summary followed by paragraphs explaining their role, collaboration
   boundaries, lifecycle, side effects, and security or trust implications where
   relevant. Avoid starting with "Class that...". Describe public attributes in
   an `Attributes:` section. Rules for specific types of classes:
   a. For exception classes, describe what the error represents rather than when
      it is raised.
   b. For pydantic models, do not describe each field in an `Attributes:` section.
      Instead, make sure that each field has an appropriate description. If field
      validators and/or serializers are used, document their purpose and behavior
      in the field description. If model validators are used, document their purpose
      and behavior in the class description in a `Model validation:` section.
10. Public module docstrings must state the module's responsibility and summarize
   its principal public types, functions, and collaboration boundary. Package
   docstrings in `__init__.py` must additionally summarize each group of
   imported or re-exported symbols. If an initializer executes statements other
   than imports, document their purpose in a separate paragraph.
11. Place a function, method, class, or module docstring as its first statement.
   In a function or method, it must appear immediately after the signature and
   before comments, nested definitions, or executable statements. Move
   explanatory comments below the docstring rather than placing a docstring
   after them.
12. For overridden methods, put a one-line docstring `See base method.` when behavior
   does not materially differ or there are no extra details, such as side effects.
   Otherwise put a full docstring.
13. Do not adjust inline comments. Do not update docstrings that are not within the
   requested scope.

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
