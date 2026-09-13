---
name: write-work-item
description: >-
  Draft or refine stories, tasks, and bugs from rough notes, requirements,
  or observed behavior. Use when asked to write a work item, ticket, user
  story, task description, bug report, or acceptance criteria. Draft by
  default; publish through manage-jira-issues only when requested.
argument-hint: '<story|task|bug> <notes or existing issue ID>'
---

# Write Work Item

Produce a concise, actionable work item. Scale detail to complexity.

## Shared Workflow

1. Identify the work-item type:
   - Story: a capability delivering value to a user or stakeholder.
   - Task: bounded technical or operational work with a concrete outcome.
   - Bug: observed behavior that differs from justified expectations.
2. Read supplied material. For existing Jira issues, retrieve the current
   issue through manage-jira-issues before proposing a revision.
3. Ask only questions whose answers materially change scope or acceptance.
   Otherwise draft immediately and list unresolved questions separately.
4. Follow the relevant approach below.
5. Check that scope is coherent and completion can be objectively verified.
   Suggest splitting independent outcomes; do not silently expand scope.
6. Return the type, title, and description, followed by any open questions.

## Story: Start With Value

- Establish who needs the capability, their problem, and the desired outcome.
- Describe the user workflow and observable behavior before implementation.
- Identify scope boundaries and relevant failure or permission scenarios.
- Write testable acceptance criteria; use Given/When/Then when helpful.
- Keep technical suggestions separate from product requirements.
- Sections: Context and Value, Desired Behavior, Scope, Acceptance Criteria.
- Title: name the capability or user outcome.

## Task: Start With The Deliverable

- Establish the concrete output and why the work is necessary.
- Identify affected components, constraints, and dependencies.
- Include an implementation checklist only when the steps are known.
- Define completion by verified results, not merely activities performed.
- Include rollout or rollback requirements when relevant.
- Sections: Objective, Scope, Deliverables, Completion Criteria, Dependencies.
  Dependencies must include at least any relevant other work items as well as 
  repositories involved.
- Title: use an action verb and a specific object.

## Bug: Start With Evidence

- Capture expected and actual behavior and the basis for the expectation.
- Record reproduction steps, inputs, environment, and frequency when known.
- State user impact and regression information without inventing severity.
- Separate observations from suspected causes; diagnosis is not required.
- Define acceptance around corrected behavior and regression coverage.
- Sections: Summary and Impact, Reproduction, Expected Behavior,
  Actual Behavior, Environment and Evidence, Acceptance Criteria.
- Title: describe the symptom and triggering condition.

## Guardrails

- Never invent requirements, reproduction results, causes, or estimates.
- Mark missing evidence as unknown; do not present hypotheses as facts.
- Inspect repository details only when needed to substantiate a claim.
- Omit irrelevant sections and redact secrets or sensitive data.
- Do not implement code or mutate Jira unless explicitly requested.
- For publication, use manage-jira-issues for metadata and duplicate checks.