"""Auto-converter CSV→Parquet con check esistenza.

Logica:
- Legge tutti i CSV in csv/
- Per ogni CSV, check se corrispondente Parquet esiste
- Se NO → converti e salva in parquet/
- Se SÌ → skip (idempotent)
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.append(str(REPO_ROOT))

from shared.config import COT_CSV_DIR, COT_PARQUET_DIR, ensure_directories
import pandas as pd

LOGGER = logging.getLogger("cot.converter")


def csv_to_parquet(csv_path: Path, parquet_path: Path) -> Path:
    """Converti CSV a Parquet ottimizzando tipi e colonne."""
    df = pd.read_csv(csv_path, sep="\t")
    
    # Ottimizza date parsing
    date_cols = [c for c in df.columns if 'Date' in c and 'YYYY-MM-DD' in c]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
    
    # Rimuovi colonne duplicate e spazi
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.duplicated()]
    
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, index=False)
    
    LOGGER.info(f"Converted {csv_path.name} to {parquet_path.name} ({len(df):,} rows)")
    return parquet_path


def convert_all_csvs(force: bool = False) -> list[Path]:
    """Converte tutti i CSV in Parquet se non esistono già."""
    ensure_directories()
    
    csv_files = sorted(COT_CSV_DIR.glob("cot_*.txt"))
    converted = []
    
    for csv_file in csv_files:
        # Naming: cot_legacy_2023.txt → legacy_futures_2023.parquet
        year = csv_file.stem.split("_")[-1]
        parquet_name = f"legacy_futures_{year}.parquet"
        parquet_path = COT_PARQUET_DIR / parquet_name
        
        if parquet_path.exists() and not force:
            LOGGER.debug(f"Skipping {csv_file.name} (Parquet exists)")
            continue
        
        converted.append(csv_to_parquet(csv_file, parquet_path))
    
    return converted


def main():
    parser = argparse.ArgumentParser(description="Auto-convert CSV to Parquet")
    parser.add_argument("--force", action="store_true", help="Re-convert even if Parquet exists")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()
    
    logging.basicConfig(level=getattr(logging, args.log_level), format='%(message)s')
    
    converted = convert_all_csvs(force=args.force)
    if converted:
        print(f"[OK] Converted {len(converted)} files to Parquet")
    else:
        print("[OK] All Parquet files already exist")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())