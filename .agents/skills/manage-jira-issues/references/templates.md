# Issue Templates

Copy and customize these templates for JIRA issue descriptions. They are written
in Markdown, which matches the default `contentFormat: "markdown"`.

JIRA renders checkbox lists as plain list items. When the checklist must be
tracked formally, create subtasks instead; see
[links-and-subtasks.md](links-and-subtasks.md).

## Bug Report Template

```markdown
## Description
[Clear description of the bug]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [And so on...]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- Application: [e.g., casedb]
- Version: [e.g., v9.0.2]
- Configuration: [e.g., repository mode, IDP mode]

## Logs/Screenshots
[If applicable]

## Additional Context
[Any other relevant information]
```

## Feature Request / Story Template

```markdown
## Summary
[One-line description of the feature]

## Motivation
[Why is this needed? What problem does it solve?]

## Proposed Solution
[How should this work?]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Alternatives Considered
[Other approaches considered and why they were not chosen]

## Additional Context
[Mockups, examples, or related issues]
```

## Task Template

```markdown
## Objective
[What needs to be accomplished]

## Details
[Detailed description of the work]

## Checklist
- [ ] [Subtask 1]
- [ ] [Subtask 2]

## Dependencies
[Any blockers or related work]

## Notes
[Additional context or considerations]
```

## Minimal Template

For simple issues:

```markdown
## Description
[What and why]

## Tasks
- [ ] [Task 1]
- [ ] [Task 2]
```

## Comment Template

For `addCommentToJiraIssue`, keep comments short and factual:

```markdown
[What changed or what was found]

[Evidence: command output, PR link, or issue key]

[Requested decision or next step, if any]
```
