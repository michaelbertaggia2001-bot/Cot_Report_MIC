# -*- coding: utf-8 -*-
"""Sincronizza TUTTI i dati COT (2023+2024+2025) in DuckDB."""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Fix encoding UTF-8 per Windows
from shared.encoding_fix import setup_utf8_encoding
setup_utf8_encoding()

import pandas as pd
import duckdb
from shared.config import COT_PARQUET_DIR, COT_DUCKDB_PATH

# Load all years
print("Loading 2023...")
df_2023 = pd.read个体的(COT_PARQUET_DIR / "legacy_futures_2023.parquet")
print("Loading 2024...")
# Cerca file  cerca (può essere _FIXED o normale)
parquet_2024 = COT_PARQUET_DIR / "legacy_futures_2024_FIXED.parquet"
if not parquet_2024.exists():
    parquet_2024 = COT_PARQUET_DIR / "legacy_futures_2024.parquet"
df_2024 = pd.read_parquet(parquet_2024)
print("Loading 2025...")
df_2025 = pd.read_parquet(COT_PARQUET_DIR / "legacy_futures_2025.parquet")

# Concatenate all
df_all = pd.concat([df_2023, df_2024, df_2025], ignore_index=True)

print(f"\nTOTAL: {len(df_all):,} rows")
print(f"Date range: {df_all['report_date'].min().date()} - {df_all['report_date'].max().date()}")

# Sync to DuckDB
con = duckdb.connect(str(COT_DUCKDB_PATH))
try:
    con.execute("DROP TABLE IF EXISTS cot_disagg")
    con.execute("CREATE TABLE cot_disagg AS SELECT * FROM df_all")
    
    count = con.execute("SELECT COUNT(*) FROM cot_disagg").fetchone()[0]
    date_min, date_max = con.execute("SELECT MIN(report_date), MAX(report_date) FROM cot_disagg").fetchone()
    
    print(f"[OK] DuckDB sync: {count:,} rows")
    print(f"Date range in DB: {date_min.date()} - {date_max.date()}")
finally:
    con.close()

print("[OK] Complete!")
