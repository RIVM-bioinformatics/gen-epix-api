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
- Type `#` in chat and select a **file / folder / symbol**
- Or **drag & drop** files/folders from the Explorer into the chat input
- Use `#selection` when you've highlighted code

**Minimum best practice:** Attach `#.github/copilot-instructions.md`, then the relevant code files you're touching.

### C) Attach minimal context
For any task:
- Attach `#.github/copilot-instructions.md` (repo architectural rules)
- Attach `#docs/00-Index.md` if you need to find architecture docs
- Attach the 1–3 code files you're changing
- Do NOT attach launch.json, changelogs, or large reference files

---

## 3) Core instruction files

**Must know**
- `.github/copilot-instructions.md` = architectural rules and security constraints
- `docs/00-Index.md` = documentation map and overview

**For specific topics, check docs/**
- See `docs/00-Index.md` for available docs on architecture, security, API design, etc.
- Each doc starts with a creation date; prefer newer docs when they disagree.

---

## 4) Golden Prompt (source of truth)

We keep the canonical “golden prompt” here:

- `.github/prompts/base_prompt.md`

**Team rule:** Don't copy/paste and fork the golden prompt into random docs. If we want to improve it, update the prompt file so everyone benefits.

### How to use it in Copilot Chat (recommended pattern)

1) Attach the golden prompt file:
- Add `#.github/prompts/base_prompt.md`

2) Attach the docs entrypoint (and the relevant deep dive):
- Always attach `#docs/00-Index.md`
- Then attach the most relevant deep dive(s) for the task

3) Attach the code you’ll touch:
- At least the primary file(s), or use `@workspace` if you’re not sure yet

4) Ask your task clearly

### Task “wrappers” that work well (copy/paste)

#### A) Implement a change (safe default)
> Use the golden prompt in `#.github/prompts/base_prompt.md`.  
> Consult `#docs/00-Index.md` first (check doc creation dates), then the relevant deep dive(s).  
> Task: [PASTE TASK HERE]

#### B) Quick orientation (where does this live?)
> @workspace Use the golden prompt in `#.github/prompts/base_prompt.md`.  
> Start from `#docs/00-Index.md`.  
> Question: Where is [X] implemented? Give me the owning service/module, the top 3–5 files/symbols, and the expected flow.

#### C) Docs vs code mismatch check
> Use the golden prompt in `#.github/prompts/base_prompt.md`.  
> Compare `#[DOC_NAME.md]` (note creation date) against the current implementation.  
> Output: mismatches, evidence (paths/symbols), and suggested doc updates (sections to change).


---

## 5) Common tasks

### Task: Add an endpoint
> Attach `#.github/copilot-instructions.md` + the router file.  
> I need to add an endpoint for ____.  
> Show the minimal changes: router, command, policy, and tests.

### Task: Change auth behavior
> Attach `#.github/copilot-instructions.md` + the policy/auth code.  
> Change: ____.  
> List affected policies, where checks occur, and state IDPS/MOCK/NONE implications.

### Task: Find something in the codebase
> @workspace Where is ____ implemented?  
> Give me: the owning module, top 3–5 files/symbols, and the flow.

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
- Attach `#docs/00-Index.md` + the relevant deep dive doc explicitly.

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

## 9) File organization

- **`.github/copilot-instructions.md`** = architectural rules and constraints
- **`.github/prompts/base_prompt.md`** = response format and evidence requirements (referenced by copilot-instructions.md)
- **`docs/ai_agent_guide.md` (this file)** = practical "how to prompt" guidance for humans
- **`AGENTS.md`** = subagent roster and how to invoke them

---

## 10) Quick troubleshooting

**Missing context** → Attach the file explicitly with `#file.md` or drag & drop.

**No evidence cited** → Reply: "Cite file paths + symbols + line ranges. If not found, add 'Suspected Stale Documentation' section."

**Wrong pattern suggested** → Reply: "Show the pattern in current code with precedent."

**Made-up endpoints/config** → Reply: "Search workspace. If not found, list as Suspected Stale Documentation."