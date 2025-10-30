# -*- coding: utf-8 -*-
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.append(str(REPO_ROOT))

# Fix encoding UTF-8 per Windows
from shared.encoding_fix import setup_utf8_encoding
setup_utf8_encoding()

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
