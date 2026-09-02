#!/usr/bin/env bash
# Start the local SQL Server stack, bring every Alembic schema to head, and
# expose the databases through DbGate. Safe to rerun: initialization and
# Alembic upgrades are idempotent, and database volumes are preserved.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: scripts/start-sql-stack.sh [--idp]

Starts the local SQL Server database, applies all Alembic migrations, starts
the APIs and DbGate. Use --idp to include the mock OIDC provider.

The script preserves existing Docker volumes. To reset all local SQL data:
  docker compose -f docker-compose.sql.yml down -v
EOF
}

compose_file="docker-compose.sql.yml"

case "${1:-}" in
    "") ;;
    --idp) compose_file="docker-compose.sql.idp.yml" ;;
    --help|-h)
        usage
        exit 0
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac

if ! docker info >/dev/null 2>&1; then
    echo "Docker is not running or is not reachable." >&2
    exit 1
fi

compose=(docker compose -f "$compose_file")

"${compose[@]}" build
"${compose[@]}" up -d --wait lsp_sql
"${compose[@]}" run --rm init-db

for migration in commondb casedb seqdb omopdb; do
    "${compose[@]}" run --rm "migrate-$migration"
done

# The migrations above have finished successfully, so start the APIs without
# recreating the one-shot dependency services. CaseDB needs SeqDB to be ready.
"${compose[@]}" up -d --no-deps --wait seqdb omopdb dbgate
"${compose[@]}" up -d --no-deps --wait casedb

echo
echo "Local stack is ready. DbGate: http://127.0.0.1:3000"
