# Settings Manager

> 15 nodes · cohesion 0.16

## Key Concepts

- **SettingsManager** (10 connections) — `gen_epix/commondb/config/settings_manager.py`
- **settings_manager.py** (4 connections) — `gen_epix/commondb/config/settings_manager.py`
- **.load_settings()** (4 connections) — `gen_epix/commondb/config/settings_manager.py`
- **Dynaconf** (3 connections)
- **.get_setting()** (3 connections) — `gen_epix/commondb/config/settings_manager.py`
- **.parse_settings_files_from_string()** (3 connections) — `gen_epix/commondb/config/settings_manager.py`
- **.__init__()** (2 connections) — `gen_epix/commondb/config/settings_manager.py`
- **.settings()** (2 connections) — `gen_epix/commondb/config/settings_manager.py`
- **Any** (1 connections)
- **Settings manager for handling application settings.** (1 connections) — `gen_epix/commondb/config/settings_manager.py`
- **Get setting value by dot-notation path. Args: key_path: Dot-separated path to…** (1 connections) — `gen_epix/commondb/config/settings_manager.py`
- **Parse settings file from comma separated string.** (1 connections) — `gen_epix/commondb/config/settings_manager.py`
- **Manages application settings with environment variable overrides.** (1 connections) — `gen_epix/commondb/config/settings_manager.py`
- **Initialize settings manager.** (1 connections) — `gen_epix/commondb/config/settings_manager.py`
- **Load settings from one or more settings file(s) specified either as a list or…** (1 connections) — `gen_epix/commondb/config/settings_manager.py`

## Relationships

- [App Composition & Startup](App_Composition_&_Startup.md) (4 shared connections)

## Source Files

- `gen_epix/commondb/config/settings_manager.py`

## Audit Trail

- EXTRACTED: 20 (95%)
- INFERRED: 1 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*