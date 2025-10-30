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
from shared.encoding_utils import format_number_ascii

# Mapping colonne per normalizzazione
LEGACY_COLUMN_MAP = {
    "As of Date in Form YYYY-MM-DD": "report_date",
    "CFTC Contract Market Code": "contract_market_code",
    "Market and Exchange Names": "market_and_exchange",
    "Noncommercial Positions-Long (All)": "noncommercial_long",
    "Noncommercial Positions-Short (All)": "noncommercial_short",
    "Change in Noncommercial-Long (All)": "noncommercial_long_change",
    "Change in Noncommercial-Short (All)": "noncommercial_short_change",
}

def normalize_columns_if_needed(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizza le colonne se necessario (se non già normalizzate)."""
    # Verifica se già normalizzato
    if "report_date" in df.columns:
        return df
    
    # Normalizza le colonne
    df.columns = df.columns.str.strip()
    rename_map = {}
    for col in df.columns:
        if col in LEGACY_COLUMN_MAP:
            rename_map[col] = LEGACY_COLUMN_MAP[col]
    
    df = df.rename(columns=rename_map)
    
    # Converti report_date in datetime se presente
    if "report_date" in df.columns:
        df["report_date"] = pd.to_datetime(df["report_date"], format="%Y-%m-%d", errors="coerce")
        df = df.dropna(subset=["report_date"])
    
    return df

# Carica dinamicamente tutti i file Parquet disponibili
parquet_files = sorted(COT_PARQUET_DIR.glob("legacy_futures_*.parquet"))

if not parquet_files:
    print("[ERROR] Nessun file Parquet trovato in", COT_PARQUET_DIR)
    print("Esegui prima: python scripts/cot/update_cot_pipeline.py")
    sys.exit(1)

# Carica tutti i file disponibili
dfs = []
for parquet_file in parquet_files:
    year = parquet_file.stem.split("_")[-1]
    print(f"Loading {year}...")
    try:
        df = pd.read_parquet(parquet_file)
        df = normalize_columns_if_needed(df)
        dfs.append(df)
        print(f"  -> {format_number_ascii(len(df))} righe caricate")
    except Exception as e:
        print(f"  -> [ERROR] Impossibile caricare {parquet_file.name}: {e}")

if not dfs:
    print("[ERROR] Nessun file Parquet caricato correttamente")
    sys.exit(1)

# Concatenate all
df_all = pd.concat(dfs, ignore_index=True)

print(f"\nTOTAL: {format_number_ascii(len(df_all))} rows")
print(f"Date range: {df_all['report_date'].min().date()} - {df_all['report_date'].max().date()}")

# Sync to DuckDB
con = duckdb.connect(str(COT_DUCKDB_PATH))
try:
    con.execute("DROP TABLE IF EXISTS cot_disagg")
    con.execute("CREATE TABLE cot_disagg AS SELECT * FROM df_all")
    
    count = con.execute("SELECT COUNT(*) FROM cot_disagg").fetchone()[0]
    date_min, date_max = con.execute("SELECT MIN(report_date), MAX(report_date) FROM cot_disagg").fetchone()
    
    print(f"[OK] DuckDB sync: {format_number_ascii(count)} rows")
    print(f"Date range in DB: {date_min.date()} - {date_max.date()}")
finally:
    con.close()

print("[OK] Complete!")
