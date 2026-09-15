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

Produce a concise, actionable work item. Scale detail to complexity. The user 
may ask to update an already existing work item rather than create a new one.

## Shared Workflow

1. Identify the work-item type:
   - Story: a capability delivering value to a user or stakeholder.
   - Task: bounded technical or operational work with a concrete outcome.
   - Bug: observed behavior that differs from justified expectations.
2. Read supplied material, including the original title as evidence of the
  intended outcome. For existing Jira issues, retrieve the current issue
  through manage-jira-issues before proposing a revision.
3. Extract and reorganize, rather than wrap the source in a template:
  - Classify information as purpose, desired behavior, scope, dependencies,
    implementation, or acceptance criteria, using the sections for the item type.
  - Place each passage in its appropriate section without needless duplication.
  - Do not paste the entire source under Implementation or nest an existing
    work-item structure inside another.
4. When source material is minimal or missing:
  - Ask only targeted questions about material unresolved decisions; do not
    speculate or append a standard questionnaire to every item.
  - Keep clarification questions outside the publishable description unless
    the user requests them there.
  - Do not invent implementation details, dependencies, or acceptance criteria.
  - Omit unsupported sections or briefly mark them as unknown. For batch drafts,
    follow the user's convention for blank, omitted, or marked unknown sections.
  - Assume sparse input is intentional until the user provides more context.
  - Do not silently expand scope.
5. Check that scope is coherent and completion can be objectively verified.
  Suggest splitting independent outcomes into separate work items.
6. Write the work item following the relevant approach below for Stories,
  Tasks, and Bugs.
7. Check the draft: each populated section must contain actual work-item
  information or an allowed brief unknown marker, each source passage must be
  in the right section, and no unsupported requirements may have been added.


## Story

- Title: name the capability or user outcome.
- Description sections:
  - Context and Value. Establish who needs the capability and for what purpose.
  - Desired Behavior. Describe the intended user workflow and observable 
    behavior before implementation. Describe failure modes and potential edge 
    cases.
  - Scope. List known affected components, repositories and constraints directly.
    Avoid generic disclaimers such as "Limited to the source item."
  - Dependencies. Must include any relevant other work items that this one 
    depends on (referenced by ID), as well as repository dependencies and human
    coordination or stakeholder needs supported by the source. Merely affected
    repositories belong in Scope. Do not include information that is not an
    actual dependency, such as sprint assignments or status information.
    Use "None identified" when no dependencies are stated and "None" only when
    their absence is confirmed. Do not refer to the export or drafting process.
  - Implementation. Include only when requested by the user or already present
    in a rough form in the source material or existing issue. Describe how to 
    implement the desired behavior. Needs to contain detail corresponding to the
    complexity of the implementation and the experience of the assignee in this
    matter. If the latter is not known, explain supplied details for a junior
    assignee without inventing technical choices. Use numbered steps, with
    sub-steps as needed, when an implementation sequence is known. For
    investigations or undecided approaches, preserve relevant discussion points
    and references without manufacturing a step-by-step plan. A single
    implementation reference does not require a list. Any code references must
    be between backticks (`) or equivalent for proper formatting.
  - Acceptance Criteria. Define completion by verified results, not merely 
    activities performed. Explicitly requested behavior, including in the title,
    may be restated as an observable result; this is not inventing a requirement.
    Do not add unprovided thresholds, technical choices, edge cases, or guarantees.
    Move supplied criteria here, preserving their meaning and conditional
    language. Keep this section self-contained instead of instructing the reader
    to "preserve and verify" criteria located elsewhere.

## Task

- Title: start with an action verb and a specific object.
- Description sections:
  - Objective. Establish the concrete output and why the work is necessary.
    Use the stated problem, motivation, and intended outcome from the title and
    description. Never substitute generic text such as "Deliver the outcome
    described in the source item." Include rollout or rollback requirements
    when relevant and supported by the source.
  - Scope. Same as for Stories.
  - Dependencies. Same as for Stories.
  - Implementation. Same as for Stories.
  - Acceptance Criteria. Same as for Stories.

## Bug

- Define acceptance around corrected behavior and regression coverage.
- Title: describe the symptom and triggering condition.
- Sections:
  - Summary and Impact. State user impact and regression information without 
    inventing severity.
  - Reproduction. Record reproduction steps, inputs, environment, and frequency 
    when known. Include screenshots if possible in case of visual bugs.
  - Expected Behavior. Describe the behavior that is expected under the given
    conditions.
  - Actual Behavior. Describe the behavior that actually occurs under the given
    conditions.
  - Potential causes. Include only when requested by the user. These should be
    based on a quick first analysis of the description versus the codebase. 
    When no potential causes are identified, state "None found". If not 
    requested by the user, state "Not investigated".
  - Acceptance Criteria. Same as for Stories.

## Guardrails

- Never invent requirements, reproduction results, causes, or estimates.
- Handle missing evidence using the unknown-section convention above; do not
  present hypotheses as facts.
- Inspect repository details only when needed to substantiate a claim.
- Omit irrelevant sections and redact secrets or sensitive data.
- Replace incidental personal names with relevant roles when identity is
  unnecessary to understand the work. Preserve names that identify an owner,
  stakeholder, or coordination dependency.
- For samples or demonstrations:
  - Clearly distinguish between example content and speculative additions
  - Note assumptions (e.g., "Assumes uv branch contains X based on name alone")
  - Or: when creating instructional samples, use items with sufficient 
    existing description to support the full format without speculation
- Do not implement code or mutate Jira unless explicitly requested.
- For publication, use manage-jira-issues for metadata and duplicate checks.
