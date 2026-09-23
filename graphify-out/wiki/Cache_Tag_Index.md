# Cache Tag Index

> 31 nodes · cohesion 0.07

## Key Concepts

- **MemoryTagIndex** (17 connections) — `gen_epix/fastapp/cache/tag.py`
- **TagIndex** (14 connections) — `gen_epix/fastapp/cache/tag.py`
- **tag.py** (12 connections) — `gen_epix/fastapp/cache/tag.py`
- **test_retagging_a_key_drops_its_previous_tags()** (3 connections) — `test/fastapp/unit/cache/test_fastapp_cache_invalidation.py`
- **test_the_tag_index_keeps_both_directions_consistent()** (3 connections) — `test/fastapp/unit/cache/test_fastapp_cache_invalidation.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/cache/tag.py`
- **ABC** (2 connections)
- **.add()** (2 connections) — `gen_epix/fastapp/cache/tag.py`
- **.clear()** (2 connections) — `gen_epix/fastapp/cache/tag.py`
- **.discard_key()** (2 connections) — `gen_epix/fastapp/cache/tag.py`
- **.keys_for()** (2 connections) — `gen_epix/fastapp/cache/tag.py`
- **.pop_tag()** (2 connections) — `gen_epix/fastapp/cache/tag.py`
- **.tags()** (2 connections) — `gen_epix/fastapp/cache/tag.py`
- **.add()** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **.clear()** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **.discard_key()** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **.keys_for()** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **.pop_tag()** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **.tags()** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **Tag indexing for invalidation that does not need the key. A writer rarely knows…** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **Forget `key` and remove it from every tag.** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **Remove `tag` and return the keys that carried it.** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **Forget every association.** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **Return the tags currently known to the index.** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- **Encapsulates keeping tag associations in process memory. The index holds both…** (1 connections) — `gen_epix/fastapp/cache/tag.py`
- *... and 6 more nodes in this community*

## Relationships

- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (7 shared connections)
- [Cache Backend Interface](Cache_Backend_Interface.md) (4 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (3 shared connections)
- [Cache Region Configuration](Cache_Region_Configuration.md) (2 shared connections)
- [Cache Region](Cache_Region.md) (2 shared connections)
- [Cache Decorator & Key Generation](Cache_Decorator_&_Key_Generation.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/tag.py`
- `test/fastapp/unit/cache/test_fastapp_cache_invalidation.py`

## Audit Trail

- EXTRACTED: 49 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*