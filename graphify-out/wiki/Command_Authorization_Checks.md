# Command Authorization Checks

> 7 nodes · cohesion 0.33

## Key Concepts

- **.is_allowed()** (6 connections) — `gen_epix/commondb/policies/has_system_outage_policy.py`
- **._is_permitted()** (5 connections) — `gen_epix/commondb/policies/has_system_outage_policy.py`
- **cached** (2 connections)
- **User** (1 connections)
- **Determine whether a command may proceed under the current outage state. Outage…** (1 connections) — `gen_epix/commondb/policies/has_system_outage_policy.py`
- **Determine whether a user has permission to administer an outage. Args:…** (1 connections) — `gen_epix/commondb/policies/has_system_outage_policy.py`
- **Determine whether no active outage currently restricts requests. Returns: True…** (1 connections) — `gen_epix/commondb/policies/has_system_outage_policy.py`

## Relationships

- [Casedb Policy Adapters](Casedb_Policy_Adapters.md) (2 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/policies/has_system_outage_policy.py`

## Audit Trail

- EXTRACTED: 10 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*