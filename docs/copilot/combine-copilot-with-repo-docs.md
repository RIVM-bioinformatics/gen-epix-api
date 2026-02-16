# Copilot Chat + Repo Docs Guide (Team)

This repo includes a set of system docs (architecture, workflows, deep dives) designed to give **GitHub Copilot Chat in VS Code** high-signal context so it can answer and generate changes that match how this codebase actually works.

> Note: Each doc starts with a **creation date on the first line**. Use it as a freshness hint.

---

## 1) The one rule

**Docs guide, code decides.**  
Use docs to find the right places and constraints quickly, but if docs conflict with current implementation, **trust the code**, then propose updating docs.

---

## 2) How to give Copilot Chat the right context (VS Code)

Copilot Chat is strongest when you deliberately attach the *right* context rather than hoping it “reads the whole repo.”

### A) Start broad when needed
Use **workspace context** for questions like:
- “Where is authentication handled?”
- “How do I add a new API endpoint?”
- “What module owns X?”

In Copilot Chat, prefix your prompt with:
- `@workspace …`

### B) Attach the relevant docs and files
When you need Copilot to follow our documented design, add explicit references:
- Type `#` in chat and select a **file / folder / symbol** (e.g., `#0_System-Documentation-Index.md`)
- Or **drag & drop** files/folders from the Explorer into the chat input
- Use `#selection` when you’ve highlighted code
- Use `#editor` when the current open file matters

**Minimum best practice for non-trivial tasks:** attach the doc(s) + the primary code file(s) you’re touching.

---

## 3) Which doc to use (quick map)

**Always start here**
- `0_System-Documentation-Index.md` (the map of the system and links to deep dives)

**Common tasks → recommended deep dive**
- Architecture / boundaries / responsibilities → `Architecture-Principles.md`, `High-Level-Architecture-Deep-Dive.md`
- AuthN/AuthZ / policies / roles → `Authorization-Authentication-Deep-Dive.md`
- API contracts / endpoints / request flow → `API-Endpoints-Deep-Dive.md`
- Contributing / PR flow / local dev conventions → `Contribution-Workflow.md`, `Local-Development-Deep-Dive.md`
- Release / deploy behavior → `Deployment-Release-Process-Deep-Dive.md`
- Adding extensions / plugins / new modules → `Extending-the-System.md`

---

## 4) The “Golden Prompt” (copy/paste into Copilot Chat)

Use this prompt when you want Copilot to combine docs + code and keep results aligned with the repo’s design.

### ✅ Golden Prompt

You are my repo assistant inside VS Code Copilot Chat. Use repository docs as navigation + constraints, and use the codebase as the source of truth.

Docs workflow:
1) Start from `0_System-Documentation-Index.md` to identify the most relevant doc(s) for this task.
2) For every doc you consult, read the first-line creation date and treat it as a freshness hint. Prefer newer docs when they disagree.
3) If a doc makes a claim, verify it in code/config where possible. If docs and code disagree, explicitly state:
   - “Docs say X, code shows Y” and recommend whether to update docs or code.

Evidence requirements:
- When stating behavior/architecture, cite concrete repo evidence: file paths + symbols (and line ranges when possible).
- Don’t invent endpoints, config keys, or module responsibilities. If unsure, ask to inspect specific files or search the workspace.

Output format:
1) What I consulted (docs + key code files)
2) Answer / plan (clear steps)
3) Patch (only if requested): minimal diff-style snippet + where it goes
4) Risks / assumptions (anything uncertain, stale, or not verified)

Task:
[PASTE TASK HERE]

---

## 5) Recommended team setup (optional but high impact)

These steps make Copilot behave consistently across the team.

### A) Add a repo-level Copilot instruction file
Create this file:

- `.github/copilot-instructions.md`

Suggested content (copy/paste):

You are working in this repository. Follow these rules:

- Use `0_System-Documentation-Index.md` as the starting point for system understanding.
- Respect the first-line creation date on docs as a freshness hint.
- Docs guide; code decides. If docs conflict with code, call it out and prefer code.
- When claiming behavior or architecture, include evidence: file paths + symbols (+ line ranges if possible).
- Avoid invented endpoints/config/behavior. Verify in repo or clearly label as an assumption.
- Prefer minimal, localized changes that match existing patterns.

### B) Add a reusable “Golden Prompt” as a VS Code prompt file
Create this file:

- `.github/prompts/golden-docs.prompt.md`

Suggested content:

Title: Golden Prompt — Docs + Code Evidence

You are my repo assistant inside VS Code Copilot Chat. Use repository docs as navigation + constraints, and use the codebase as the source of truth.

Docs workflow:
1) Start from `0_System-Documentation-Index.md` to identify the most relevant doc(s) for this task.
2) For every doc you consult, read the first-line creation date and treat it as a freshness hint. Prefer newer docs when they disagree.
3) If a doc makes a claim, verify it in code/config where possible. If docs and code disagree, explicitly state:
   - “Docs say X, code shows Y” and recommend whether to update docs or code.

Evidence requirements:
- When stating behavior/architecture, cite concrete repo evidence: file paths + symbols (and line ranges when possible).
- Don’t invent endpoints, config keys, or module responsibilities. If unsure, ask to inspect specific files or search the workspace.

Output format:
1) What I consulted (docs + key code files)
2) Answer / plan (clear steps)
3) Patch (only if requested): minimal diff-style snippet + where it goes
4) Risks / assumptions (anything uncertain, stale, or not verified)

Task:
[PASTE TASK HERE]

---

## 6) Example prompts (fast starters)

### “Where is X implemented?”
@workspace Where is authentication handled? Please consult #0_System-Documentation-Index.md first, then show the key files and flow.

### “Implement a change safely”
Consult #0_System-Documentation-Index.md and the relevant deep dive docs. I need to add a new API endpoint for ____. Propose the minimal changes and point to the exact files/symbols to edit.

### “Docs/code mismatch check”
Compare #Authorization-Authentication-Deep-Dive.md with the current auth implementation in the repo. List any mismatches and suggest doc updates.

---

## 7) Good hygiene

- When you change behavior, consider updating docs in the same PR.
- If you’re unsure whether a doc is still accurate, ask Copilot to verify against the codebase and report differences.
- Keep prompts specific: attach the doc(s) + the touched code files.
