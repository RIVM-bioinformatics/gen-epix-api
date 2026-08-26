# Repository Architecture Docs

> 8 nodes · cohesion 0.25

## Key Concepts

- **BaseRepository (abstract)** (5 connections) — `docs/02a-Fastapp-Framework.md`
- **Architectural Constraints table** (3 connections) — `docs/09-Constraints-and-Open-Questions.md`
- **BaseService** (2 connections) — `docs/02a-Fastapp-Framework.md`
- **Repository Modes (DICT_DEMO/EMPTY, SA_SQLITE_DEMO/EMPTY, SA_SQL)** (2 connections) — `docs/05-Configuration-and-Runtime.md`
- **Copilot Chat + Repo Docs Guide** (2 connections) — `docs/ai_agent_guide.md`
- **Layer Boundaries principle** (1 connections) — `docs/02-Architecture.md`
- **DictRepository (in-memory backend)** (1 connections) — `docs/02a-Fastapp-Framework.md`
- **SARepository (SQLAlchemy backend)** (1 connections) — `docs/02a-Fastapp-Framework.md`

## Relationships

- [FastAPI App Composition Root](FastAPI_App_Composition_Root.md) (1 shared connections)
- [RBAC Command Execution Model](RBAC_Command_Execution_Model.md) (1 shared connections)
- [Documentation Index](Documentation_Index.md) (1 shared connections)

## Source Files

- `docs/02-Architecture.md`
- `docs/02a-Fastapp-Framework.md`
- `docs/05-Configuration-and-Runtime.md`
- `docs/09-Constraints-and-Open-Questions.md`
- `docs/ai_agent_guide.md`

## Audit Trail

- EXTRACTED: 9 (90%)
- INFERRED: 1 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*