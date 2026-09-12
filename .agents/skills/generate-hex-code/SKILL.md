---
name: generate-hex-code
description: "Generate cryptographically random, collision-checked 8-hex-char codes for this codebase's short-code conventions - log/diagnostic message codes (App.create_log_message, create_static_log_message, exception codes like exc.NoResultsError), and gen_epix.etl.model.Result subclass discriminators (ID, COMPLETED_CODE). Use whenever a new one of these codes is needed - never hand-type or pattern-invent one (e.g. sequential nibbles like \"d4e5f6a7\") since low-entropy hand-made codes are easy to collide or reuse by accident, and this codebase already has hundreds of them."
argument-hint: "Optional: number of codes needed (default 5)"
---

# Hex code generator

This codebase uses short 8-hex-character strings as codes in two related
places:

- **Log/diagnostic/exception codes** — the first argument to
  `App.create_log_message(...)`, `App.create_static_log_message(...)`,
  `app.logger.info(app.create_log_message(code, msg, ...))`, and exception
  constructors like `exc.NoResultsError(code)`, `exc.ServiceException(code,
  msg)`. Used throughout `gen_epix/` (600+ occurrences outside `gen_epix/etl/`
  alone) so each log line / raised exception can be grepped by its code.
- **`gen_epix.etl.model.Result` subclass discriminators** —
  `ID: ClassVar[str]`, the polymorphic-deserialization key registered in
  `Result._SUBCLASS_REGISTRY` (must be globally unique across every `Result`
  subclass in every repo that imports `gen_epix.etl`: this repo, `lsp-data`,
  `idsdb`, `juno-seqdb-etl`, ...), and `COMPLETED_CODE` (a completion-log
  code, less severe to collide but still meant to stay individually
  searchable).

Never hand-type or invent one of these by eye. A pattern like `"d4e5f6a7"`
(ascending nibbles) *looks* like a random hex string but isn't — it's easy to
produce by accident when typing "something hex-looking" quickly, and easy to
collide with another hand-typed code for the same reason. Always generate
with `secrets.token_hex()`, not by eyeballing hex digits.

## Procedure

1. Run the collision-checked generator:

   ```bash
   python .agents/skills/hex-code/scripts/generate_hex_codes.py --count 5
   ```

   It scans every `.py` file under the repo root for existing 8-hex-char
   string literals — covers log codes, exception codes, and `Result`
   `ID`/`COMPLETED_CODE` ClassVars alike, since they're all the same
   `"[0-9a-f]{8}"` literal shape — and only prints codes that don't collide
   with anything already in the codebase.

2. If you're adding a code to an *external* repo (`idsdb`, `lsp-data`,
   `juno-seqdb-etl`) rather than here, run the script with `--root` pointed
   at that repo's checkout instead, so the collision scan covers that repo's
   own already-used codes too — this script only sees one repo at a time,
   so cross-repo collisions aren't caught automatically. This matters most
   for `Result` subclass `ID`s (registry is shared across repos); for a
   plain log/exception code, a same-repo scan is normally enough.

3. Pick codes off the top of the printed list, in order — don't cherry-pick
   for "look" (e.g. avoiding ones that look like real words); any printed
   code is equally safe to use.

