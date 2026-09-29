# Domain Package Layout

> 8 nodes · cohesion 0.25

## Key Concepts

- **fastapp shared application framework** (8 connections) — `AGENTS.md`
- **casedb domain** (2 connections) — `AGENTS.md`
- **commondb shared package** (2 connections) — `AGENTS.md`
- **pydantic** (2 connections) — `requirements.txt`
- **filter and transform support packages** (1 connections) — `AGENTS.md`
- **omopdb domain** (1 connections) — `AGENTS.md`
- **seqdb domain** (1 connections) — `AGENTS.md`
- **Shared /v1 router composition pattern** (1 connections) — `AGENTS.md`

## Relationships

- [Agent Conventions & Guides](Agent_Conventions_&_Guides.md) (2 shared connections)
- [OAuth Provider Test Harness](OAuth_Provider_Test_Harness.md) (1 shared connections)
- [App Configuration & Startup](App_Configuration_&_Startup.md) (1 shared connections)

## Source Files

- `AGENTS.md`
- `requirements.txt`

## Audit Trail

- EXTRACTED: 7 (64%)
- INFERRED: 4 (36%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*