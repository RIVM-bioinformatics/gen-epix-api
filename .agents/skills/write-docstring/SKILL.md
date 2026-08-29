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
4. Always add a docstring. When it documents a public API, nontrivial code, or
   non-obvious behavior, make a complete docstring. Do not skip docstrings that
   add no information, such as `"""Tests for foo.bar."""`, but keep them one line
   long. Test module docstrings must be created, but can be very brief.
5. Describe what the code does and how callers should use it, not its internal
   implementation. Mention implementation details only when callers need to
   know them, such as whether an argument is mutated in place.
6. Write the docstring using triple double quotes. Keep every line at or under
   88 characters. Make the summary one physical sentence ending in `.`, `?`, or
   `!`. If the docstring has more content, put one blank line after the summary.
7. Add `Args:`, `Returns:`, `Yields:`, or `Raises:` sections only when they add
   meaning beyond the type hints. Do not restate obvious types. Use a consistent
   hanging indent of two or four spaces within the file. Document only
   interface-relevant exceptions under `Raises:`.
8. For classes, avoid starting with "Class that...". Describe public attributes
   in an `Attributes:` section. Rules for specific types of classes:
   a. For exception classes, describe what the error represents rather than when
      it is raised.
   b. For pydantic models, do not describe each field in an `Attributes:` section.
      Instead, make sure that each field has an appropriate description. If field
      validators and/or serializers are used, document their purpose and behavior
      in the field description. If model validators are used, document their purpose
      and behavior in the class description in a `Model validation:` section.
9. For overridden methods, put a one-line docstring `See base method` when behavior
   does not materially differ or there are no extra details, such as side effects.
   Otherwise put a full docstring.
10. Do not adjust inline comments. Do not update docstrings that are not within the
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
