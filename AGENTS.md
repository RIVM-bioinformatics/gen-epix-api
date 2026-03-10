# Gen-EpiX Agent Configuration

## Plan Directory

All plan files should be stored in: `.github/plans/`

## Agent Roster

Agent definitions live in `.github/agents/`. The following agents are available:

### Conductor Agents

| Agent | File | Model | Description |
|-------|------|-------|-------------|
| **Atlas** | `.github/agents/Atlas.agent.md` | Claude Sonnet 4.5 | Orchestrates the full Planning → Implementation → Review → Commit cycle. Delegates to all subagents. |
| **Prometheus** | `.github/agents/Prometheus.agent.md` | GPT-5.2 | Autonomous planner that researches requirements and writes comprehensive implementation plans, then hands off to Atlas. |

### Subagents

| Agent | File | Model | Description |
|-------|------|-------|-------------|
| **Oracle** | `.github/agents/Oracle.agent.md` | GPT-5.2 | Research/planning subagent. Gathers comprehensive context and returns structured findings. Can delegate to Explorer. |
| **Explorer** | `.github/agents/Explorer.agent.md` | Gemini 3 Flash | Codebase exploration subagent. Quickly locates files, usages, and dependencies. Read-only; no edits or commands. |
| **Sisyphus** | `.github/agents/Sisyphus.agent.md` | Claude Sonnet 4.5 | Implementation subagent. Executes focused coding tasks following strict TDD (red → green → refactor). |
| **Code-Review** | `.github/agents/Code-Review.agent.md` | GPT-5.2 | Code review subagent. Verifies implementation correctness, test coverage, and code quality. Returns APPROVED / NEEDS_REVISION / FAILED. |
| **Frontend-Engineer** | `.github/agents/Frontend-Engineer.agent.md` | Gemini 3 Pro | Frontend/UI specialist. Implements user interfaces, styling, responsive layouts, and frontend features with TDD. |

## Delegation Graph

```
User
 ├── Prometheus  ──(research)──▶  Explorer, Oracle
 │        │
 │        ▼
 └── Atlas (conductor)
      ├── Explorer      (codebase discovery)
      ├── Oracle         (deep research)
      ├── Sisyphus       (backend implementation)
      ├── Frontend-Engineer (UI implementation)
      └── Code-Review    (post-implementation review)
```

## Conventions

- **TDD is mandatory** for all implementation phases (Sisyphus, Frontend-Engineer).
- **Atlas pauses for user approval** after presenting a plan and after each phase commit.
- **Prometheus works autonomously** through research, only pausing when the plan is complete.
- **Explorer is read-only** — it never edits files or runs commands.
- **Code-Review never implements fixes** — it only reports findings.
