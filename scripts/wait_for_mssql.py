"""Wait until SQL Server accepts connections, then create the seqdb database.

Usage: python scripts/wait_for_mssql.py [max_attempts]
Exit 0 on success, 1 on timeout.
"""

import sys
import time

import pyodbc

DSN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=127.0.0.1,1433;"
    "UID=sa;PWD=Your_password123;"
)
MAX_ATTEMPTS = int(sys.argv[1]) if len(sys.argv) > 1 else 20

for attempt in range(1, MAX_ATTEMPTS + 1):
    print(f"Attempt {attempt}/{MAX_ATTEMPTS}...", end=" ", flush=True)
    try:
        conn = pyodbc.connect(DSN, timeout=3)
        conn.autocommit = True
        conn.execute("IF DB_ID('seqdb') IS NULL CREATE DATABASE seqdb")
        conn.close()
        print("SQL Server ready, seqdb database exists.")
        sys.exit(0)
    except Exception:
        print("not ready yet.")
        time.sleep(10)

print("Timed out waiting for SQL Server.", file=sys.stderr)
sys.exit(1)
