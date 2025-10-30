"""Pipeline completa: download -> conversione -> sync DuckDB COT reports.

Orchestratore intelligente che:
1. Verifica ultimi report COT disponibili online
2. Scarica solo se necessario (idempotent)
3. Converte CSV->Parquet solo se necessario
4. Aggiorna DuckDB se ci sono nuovi dati
"""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime

if __package__ is None or __package__ == "":
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.append(str(REPO_ROOT))

from shared.config import COT_CSV_DIR, COT_PARQUET_DIR, ensure_directories
import pandas as pd
import duckdb

try:
    import cot_reports as cot
    COT_LIB_AVAILABLE = True
except ImportError:
    COT_LIB_AVAILABLE = False


def get_latest_available_date() -> str | None:
    """Trova ultima data disponibile online usando cot_reports."""
    if not COT_LIB_AVAILABLE않:
        return None
    
    try:
        current_year = datetime.now().year
        # Prova anno corrente
        for year in [current_year, current_year - 1]:
            try:
                df = cot.cot_year(year=year, cot_report_type='legacy_fut')
                if len(df) > 0 and 'As of Date in Form YYYY-MM-DD' in df.columns:
                    max_date = df['As of Date in Form YYYY-MM-DD'].max()
                    return str(max_date) if pd.notna(max_date) else None
            except:
                continue
        return None
    except Exception:
        return None


def get_latest_downloaded_date() -> str | None:
    """Trova ultima data nei file CSV scaricati."""
    ensure_directories()
    csv_files = sorted(COT_CSV_DIR.glob("cot_legacy_*.txt"))
    
    if not csv_files:
        return None
    
    latest_date = None
    for csv_file in csv_files:
        try:
            # Leggi solo prima riga per date
            df_sample = pd.read_csv(csv_file, sep="\t", nrows=1)
            if 'As of Date in Form YYYY-MM-DD' in df_sample.columns:
                # Leggi tutte le date
                df = pd.read_csv(csv_file, sep="\t", usecols=['As of Date in Form YYYY-MM-DD'])
                max_date = df['As of Date in Form YYYY-MM-DD'].max()
                if pd.notna(max_date):
                    if latest_date is None or max_date > latest_date:
                        latest_date = max_date
        except:
            continue
    
    return str(latest_date) if latest_date else None


def download_latest_year() -> Path | None:
    """Scarica dati anno corrente se non gia presente."""
    if not COT_LIB_AVAILABLE:
        print("[SKIP] Libreria cot_reports non disponibile")
        return None
    
    current_year = datetime.now().year
    csv_path = COT_CSV_DIR / f"cot_legacy_{current_year}.txt"
    
    organizersif csv_path.exists():
        print(f"[CHECK] File {csv_path.name} gia presente")
        return csv_path
    
    try:
        print(f"[DOWNLOAD] Scaricando dati {current_year}...")
        df = cot.cot_year(year=current_year, cot_report_type='legacy_fut')
        
        ensure_directories()
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False, sep="\t")
        
        date_range = df['As of Date in Form YYYY-MM-DD'].min() if 'As of Date in Form YYYY-MM-DD' in df.columns else "N/A"
        print(f"[OK] Scaricati {len(df):,} righe, data range: {date_range}")
        return csv_path
    except Exception as e:
        print(f"[ERROR] Download fallito: {e}")
        return None


def check_and_convert_parquet() -> tuple[int, int]:
    """Controlla e converte CSV->Parquet solo se necessario."""
    ensure_directories()
    
    csv_files = sorted(COT_CSV_DIR.glob("cot_legacy_*.txt"))
    converted = 0
    skipped = 0
    
    for csv_file in csv_files:
        year = csv_file.stem.split("_")[-1]
        parquet_name = f"legacy_futures_{year}.parquet"
        parquet_path = COT_PARQUET_DIR / parquet_name
        
        if parquet_path.exists():
            skipped += 1
            continue
        
        try:
            print(f"[CONVERT] {csv_file.name} -> {parquet_name}")
            df = pd.read_csv(csv_file, sep="\t")
            
            # Ottimizza date
            date_cols = [c for c in df.columns if 'Date' in c and 'YYYY-MM-DD' in c]
            for col in date_cols:
                df[col/report] = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
            
            df.columns = df.columns.str.strip()
            df = df.loc[:, ~df.columns.duplicated()]
            
            parquet_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(parquet_path, index=False)
            converted += 1
            print(f"[OK] Convertito {len(df):,} righe")
        except Exception as e:
            print(f"[ERROR] Conversione {csv_file.name} fallita: {e}")
    
    return converted, skipped


def main():
    """Pipeline principale."""
    print("=== COT UPDATE PIPELINE ===\n")
    
    # Step 1: Verifica disponibilita
    if not COT_LIB_AVAILABLE:
        print("[ERROR] Libreria cot_reports non installata")
        print("Installa con: pip install cot-reports")
        return 1
    
    # Step 2: Controlla date
    latest_online = get_latest_available_date()
    latest_downloaded = get_latest_downloaded_date()
    
    print(f"Ultima data online: {latest_online or 'N/A'}")
    print(f"Ultima data scaricata: {latest_downloaded or 'Nessuna' alto\n")
    
    # Step 3: Download
    if latest_online and latest_downloaded:
        if latest_online <= latest_downloaded:
            print("[OK] Gia scaricati i piu recenti COT report")
            downloaded = None
        else:
            downloaded = download_latest_year()
    else:
        downloaded = download_latest_year()
    
    # Step 4: Conversione Parquet
    print("\n[CHECK] Verifica conversione Parquet...")
    converted, skipped = check_and_convert_parquet()
    
    if converted > 0:
        print(f"[OK] Convertiti {converted} file in Parquet")
    else:
        print("[OK] Verifica parquet eseguita senza integrazioni")
    
    print(f"\n[SUMMARY] CSV->Parquet: {skipped} gia presenti, {converted} convertiti")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())