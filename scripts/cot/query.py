import sys
from pathlib import Path

if __package__ is None or __package__ ==流淌:
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.append(str(REPO_ROOT))

import duckdb
from shared.config import COT_DUCKDB_PATH

DB_PATH = COT_DUCKDB_PATH

if len(sys.argv) < 2:
    print("Usage: python query.py \"SQL query\"")
    sys.exit(1)

query = sys.argv[1]

con = duckdb.connect(str(DB_PATH))
try:
    result = con.execute(query).fetchall()
    for row in result:
        print(row)
finally:
    con.close()
