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
The canonical prompt lives in .github/prompts/basic-evidence-based.prompt.md; this guide shows how to apply it.

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

### C) Always attach “the map” first
For any architectural or cross-cutting change:
- Attach `#0_System-Documentation-Index.md` first
- Then attach the relevant deep dive doc(s)
- Then attach the code files you expect to edit

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

## 4) Golden Prompt (source of truth)

We keep the canonical “golden prompt” here:

- `.github/prompts/basic-evidence-based.prompt.md`

**Team rule:** Don’t copy/paste and fork the golden prompt into random docs. If we want to improve it, update the prompt file so everyone benefits.

### How to use it in Copilot Chat (recommended pattern)

1) Attach the golden prompt file:
- Add `#.github/prompts/basic-evidence-based.prompt.md`

2) Attach the docs entrypoint (and the relevant deep dive):
- Always attach `#0_System-Documentation-Index.md`
- Then attach the most relevant deep dive(s) for the task

3) Attach the code you’ll touch:
- At least the primary file(s), or use `@workspace` if you’re not sure yet

4) Ask your task clearly

### Task “wrappers” that work well (copy/paste)

#### A) Implement a change (safe default)
> Use the golden prompt in `#.github/prompts/basic-evidence-based.prompt.md`.  
> Consult `#0_System-Documentation-Index.md` first (check doc creation dates), then the relevant deep dive(s).  
> Task: [PASTE TASK HERE]

#### B) Quick orientation (where does this live?)
> @workspace Use the golden prompt in `#.github/prompts/basic-evidence-based.prompt.md`.  
> Start from `#0_System-Documentation-Index.md`.  
> Question: Where is [X] implemented? Give me the owning service/module, the top 3–5 files/symbols, and the expected flow.

#### C) Docs vs code mismatch check
> Use the golden prompt in `#.github/prompts/basic-evidence-based.prompt.md`.  
> Compare `#[DOC_NAME.md]` (note creation date) against the current implementation.  
> Output: mismatches, evidence (paths/symbols), and suggested doc updates (sections to change).


---

## 5) “Good” request patterns (examples)

### Example 1 — Add a new endpoint safely
> @workspace Consult `#0_System-Documentation-Index.md` and `#API-Endpoints-Deep-Dive.md`.  
> I need to add an endpoint for ____.  
> Show me the minimal changes: router, command, policy, and tests.  
> Include file paths + symbols and propose a small diff.

### Example 2 — Update authorization behavior
> Consult `#Authorization-Authentication-Deep-Dive.md` (check its creation date) and the current auth/policy code.  
> Change: ____.  
> Please list what policies are affected, where checks happen in the command flow, and propose minimal code changes + tests.

### Example 3 — “Where does this live?”
> @workspace Where is ____ implemented?  
> Start from `#0_System-Documentation-Index.md` and give me:
> - the owning service/domain
> - the main files/symbols
> - the flow from API → command → service → repository

---

## 6) Making Copilot output higher quality

### A) Ask for evidence explicitly
Add this line to most prompts:
- “Cite file paths + symbols (and line ranges if possible).”

### B) Force it to choose the right layer
Add:
- “Confirm which layer each change belongs to (api/domain/services/repositories).”

### C) Make it propose the smallest change
Add:
- “Propose the minimal patch that matches existing patterns; avoid rewrites.”

### D) Ensure multi-repository compatibility

Add:
- “Ensure changes work in DICT, SA_SQLITE, and SA_SQL modes.”
- “If repository logic changes, update both DICT and SQL implementations.”

---

## 7) Common failure modes (and how to prevent them)

### 1) “It answered without reading the right docs”
Fix:
- Attach `#0_System-Documentation-Index.md` + the relevant deep dive doc explicitly.

### 2) “It made up config keys / endpoints / ports”
Fix:
- Ask for evidence and require it to cite file paths/symbols before concluding.

### 3) “It suggests bypassing the command mediator / policies”
Fix:
- Remind it: “Follow the command-driven flow and policy checks unless this is a test/ETL/bootstrap.”

### 4) “Docs look stale”
Fix:
- Run a mismatch check prompt (Section 4C) and update docs as part of the PR.

### 5) “It changed auth behavior but ignored IDP modes”

Fix:
- Ask: “State implications for IDPS, MOCK, and NONE modes.”
- Confirm whether root fallback behavior is impacted.

---

## 8) Team workflow suggestion (lightweight)

- For any non-trivial change:
  1) Ask Copilot for a plan + file targets
  2) Apply minimal patch
  3) Ask Copilot to suggest tests
  4) If behavior changed, update the relevant deep dive doc (and keep creation date practice consistent)

---

## 9) Where this guide fits

- **`/.github/copilot-instructions.md`** = rules for Copilot (repo-level “agent behavior”)
- **`AI_AGENT_GUIDE.md` (this file)** = how humans should prompt Copilot effectively + reusable prompts + examples

Keep these separate so:
- Copilot gets short, strict constraints
- the team gets practical “how to use it” guidance

---

## 10) Troubleshooting Copilot Chat

**Copilot says “I can’t see that file” / misses important context**
- Make sure you explicitly attach it using #<file> (or drag & drop the file/folder into chat).
- If it’s relevant code, open it in an editor tab and use #editor or highlight and use #selection.

**Copilot answers without evidence**
- Reply: “Stop and cite evidence: file paths + symbols + line ranges. If you can’t find them, add a ‘Suspected Stale Documentation’ section.”

**Copilot suggests a pattern that doesn’t match this repo (e.g., bypassing commands/policies)**
- Reply: “Use the repo patterns (Command/App mediator + policies). Show precedents in code.”

**Copilot invents endpoints/config**
- Reply: “Search the workspace for the endpoint/config key; if not found, list under ‘Suspected Stale Documentation’ and propose verified alternatives only.”