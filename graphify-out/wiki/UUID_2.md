# UUID

> 12 nodes · cohesion 0.18

## Key Concepts

- **UUID** (7 connections)
- **.create_file()** (4 connections) — `gen_epix/seqdb/services/remote_app.py`
- **.retrieve_best_seq_classification_per_sample()** (4 connections) — `gen_epix/seqdb/services/remote_app.py`
- **.retrieve_best_seq_per_sample()** (4 connections) — `gen_epix/seqdb/services/remote_app.py`
- **.retrieve_best_seq_profile_per_sample()** (4 connections) — `gen_epix/seqdb/services/remote_app.py`
- **.retrieve_similar_profiles()** (4 connections) — `gen_epix/seqdb/services/remote_app.py`
- **.retrieve_seq_distance_protocol_ids()** (3 connections) — `gen_epix/seqdb/services/remote_app.py`
- **Retrieve the best sequence ID per sample ID.** (2 connections) — `gen_epix/seqdb/services/remote_app.py`
- **Upload a file and return its assigned UUID.** (1 connections) — `gen_epix/seqdb/services/remote_app.py`
- **Retrieve profile IDs similar to the given profiles within a distance threshold.** (1 connections) — `gen_epix/seqdb/services/remote_app.py`
- **Return IDs of all seq distance protocols.** (1 connections) — `gen_epix/seqdb/services/remote_app.py`
- **Retrieve the best sequence classification ID per sample ID.** (1 connections) — `gen_epix/seqdb/services/remote_app.py`

## Relationships

- [SeqdbRemoteApp](SeqdbRemoteApp.md) (6 shared connections)
- [test_seqdb_retrieve_best.py](test_seqdb_retrieve_best.py.md) (3 shared connections)
- [CrudOperation](CrudOperation.md) (1 shared connections)
- [BaseSeqdbService](BaseSeqdbService.md) (1 shared connections)
- [SeqService](SeqService.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 24 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*