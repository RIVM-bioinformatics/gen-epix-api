# ── Local development helpers ─────────────────────────────────────────────────
#
# Targets
#   restart-docker          Rebuild and restart the full stack (keeps DB volumes).
#   restart-docker-teardown Same, but wipes DB volumes first (clean slate).
#   test                    Run the full pytest suite.
#   generate-schema-migration-docs
#                           Generate the committed-friendly Alembic history
#                           pages under docs/schema_migration/.
#   calculate-distances-performance-mssql
#                           Tear down the SQL Server volume, start only lsp_sql,
#                           create the seqdb database, then run the seq-distance
#                           optimization benchmark against MSSQL.
#                           Requires pyodbc + ODBC Driver 18 for SQL Server.
#
# SQL Server credentials (docker-compose.sql.idp.yml defaults):
#   host:     127.0.0.1:1433  (use IP, not localhost — Docker binds only to IPv4)
#   user:     sa
#   password: Your_password123
#   database: seqdb
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: restart-docker restart-docker-teardown test \
        generate-schema-migration-docs calculate-distances-performance-mssql

COMPOSE_FILE = docker-compose.sql.idp.yml

MSSQL_URL = mssql+pyodbc://sa:Your_password123@127.0.0.1:1433/seqdb?driver=ODBC+Driver+17+for+SQL+Server

restart-docker:
	docker compose -f $(COMPOSE_FILE) down && \
	docker compose -f $(COMPOSE_FILE) build && \
	docker compose -f $(COMPOSE_FILE) up -d && \
	docker compose -f $(COMPOSE_FILE) logs -f

restart-docker-teardown:
	docker compose -f $(COMPOSE_FILE) down -v && \
	docker compose -f $(COMPOSE_FILE) build && \
	docker compose -f $(COMPOSE_FILE) up -d && \
	docker compose -f $(COMPOSE_FILE) logs -f

test:
	pytest --capture=fd -q --tb=short

generate-schema-migration-docs:
	mkdir -p docs/schema_migration
	for service in commondb casedb seqdb omopdb; do \
		printf '# %s Alembic migration history\n\n```text\n' "$$service" > "docs/schema_migration/$$service.md"; \
		alembic -c "gen_epix/$$service/repositories/alembic.ini" history --verbose | sed -e 's/[[:space:]]*$$//' -e 's|Path: .*/gen_epix/|Path: gen_epix/|' >> "docs/schema_migration/$$service.md"; \
		printf '```\n' >> "docs/schema_migration/$$service.md"; \
	done

calculate-distances-performance-mssql:
	docker compose -f $(COMPOSE_FILE) down -v
	docker compose -f $(COMPOSE_FILE) up -d lsp_sql
	python scripts/wait_for_mssql.py
	SEQDB_MSSQL_TEST_URL="$(MSSQL_URL)" \
	pytest test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py \
	    -m "performance and mssql" -v -s
