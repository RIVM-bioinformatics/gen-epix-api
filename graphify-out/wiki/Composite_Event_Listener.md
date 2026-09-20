# Composite Event Listener

> 7 nodes · cohesion 0.29

## Key Concepts

- **CompositeListener** (7 connections) — `gen_epix/fastapp/cache/stats.py`
- **.add()** (3 connections) — `gen_epix/fastapp/cache/stats.py`
- **.__init__()** (3 connections) — `gen_epix/fastapp/cache/stats.py`
- **.on_event()** (2 connections) — `gen_epix/fastapp/cache/stats.py`
- **Encapsulates fanning one event out to several listeners. A failing listener is…** (1 connections) — `gen_epix/fastapp/cache/stats.py`
- **Initialize a CompositeListener instance.** (1 connections) — `gen_epix/fastapp/cache/stats.py`
- **Append a listener to the notification list.** (1 connections) — `gen_epix/fastapp/cache/stats.py`

## Relationships

- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (3 shared connections)
- [Cache Backend Interface](Cache_Backend_Interface.md) (2 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/stats.py`

## Audit Trail

- EXTRACTED: 12 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*