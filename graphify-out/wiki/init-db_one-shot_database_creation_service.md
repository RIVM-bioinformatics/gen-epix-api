# init-db one-shot database creation service

> 5 nodes

## Key Concepts

- **init-db one-shot database creation service** (4 connections) — `docker-compose.sql.yml`
- **casedb service (SA_SQL mode, embedded LOCAL seqdb)** (2 connections) — `docker-compose.sql.yml`
- **seqdb service (SA_SQL mode)** (2 connections) — `docker-compose.sql.yml`
- **lsp_sql SQL Server service** (1 connections) — `docker-compose.sql.yml`
- **omopdb service (SA_SQL mode)** (1 connections) — `docker-compose.sql.yml`

## Relationships

- No strong cross-community connections detected

## Source Files

- `docker-compose.sql.yml`

## Audit Trail

- EXTRACTED: 5 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*