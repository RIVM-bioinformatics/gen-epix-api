# ── Local development helpers ─────────────────────────────────────────────────
#
# Targets
#   restart-docker          Rebuild and restart the full stack (keeps DB volumes).
#   restart-docker-teardown Same, but wipes DB volumes first (clean slate).
#   start-db                Start only SQL Server + create the casedb/seqdb/omopdb
#                           databases (docker-compose.sql.yml). This is what the
#                           SQL Server integration tests connect to; without it
#                           test/fastapp/integration/.../test_fastapp_sa_schema_mssql
#                           and the batch-size test skip themselves.
#   stop-db                 Stop SQL Server (data kept in the Docker volume).
#   test                    Run the full pytest suite.
#   calculate-distances-performance-mssql
#                           Tear down the SQL Server volume, start only lsp_sql,
#                           create the seqdb database, then run the seq-distance
#                           optimization benchmark against MSSQL.
#                           Requires pyodbc + ODBC Driver 18 for SQL Server.
#
# SQL Server credentials (docker-compose.sql*.yml defaults):
#   host:     127.0.0.1:1433  (use IP, not localhost — Docker binds only to IPv4)
#   user:     sa
#   password: Your_password123
#   database: casedb / seqdb / omopdb
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: restart-docker restart-docker-teardown start-db stop-db test \
        calculate-distances-performance-mssql

COMPOSE_FILE = docker-compose.sql.idp.yml
SQL_COMPOSE_FILE = docker-compose.sql.yml

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

start-db:
	docker compose -f $(SQL_COMPOSE_FILE) up -d --wait lsp_sql
	docker compose -f $(SQL_COMPOSE_FILE) run --rm init-db

stop-db:
	docker compose -f $(SQL_COMPOSE_FILE) stop lsp_sql

test:
	pytest --capture=fd -q --tb=short

calculate-distances-performance-mssql:
	docker compose -f $(COMPOSE_FILE) down -v
	docker compose -f $(COMPOSE_FILE) up -d lsp_sql
	python scripts/wait_for_mssql.py
	SEQDB_MSSQL_TEST_URL="$(MSSQL_URL)" \
	pytest test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py \
	    -m "performance and mssql" -v -s
