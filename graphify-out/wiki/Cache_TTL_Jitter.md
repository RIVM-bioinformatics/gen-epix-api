# Cache TTL Jitter

> 3 nodes · cohesion 0.67

## Key Concepts

- **.apply_jitter()** (3 connections) — `gen_epix/fastapp/cache/model.py`
- **Random** (2 connections)
- **Return `ttl` shortened by a random fraction of itself. Spreading expiry over a…** (1 connections) — `gen_epix/fastapp/cache/model.py`

## Relationships

- [Cache Backend Interface](Cache_Backend_Interface.md) (1 shared connections)
- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/model.py`

## Audit Trail

- EXTRACTED: 4 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*