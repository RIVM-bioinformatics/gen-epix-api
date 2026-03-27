# CLAUDE instructions

## Git interaction

- Allow git add.
- Never git push automatically.
- Always create new branches from `dev`.


## Code editing

- Do not remove comments made by user, always ask.
- Before providing a solution always look for possible ambiguities and ask the user to make a decision
- When writing comments always make them fit in 89 columns
**How to apply:** When writing or editing any comment or docstring, ensure no line exceeds 89 characters including the leading whitespace and comment marker.


## Architecture and context

- Use [docs/00-Index.md](../docs/00-Index.md) for Context of the architecture.


## Testing

- make tests compact, e.g. when checking for 3 fields try to combine them in a test with 3 assertions instead of 3 separate tests.


