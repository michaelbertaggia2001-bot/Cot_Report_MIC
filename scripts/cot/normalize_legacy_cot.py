"""Normalize raw CFTC Legacy Futures COT reports to analytics-ready data.

Legacy format: Noncommercial (Large Speculators) + Commercial positions
as shown in the screenshot from Tradingster (market code 090741 - Canadian Dollar).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd

if __package__ is None or __package__ == "":
    REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(REPO_ROOT) not in sys.path:
        sys.path.append(str(REPO_ROOT))

from shared.config import COT_PARQUET_DIR, COT_RAW_DIR, ensure_directories


LOGGER = logging.getLogger("cot.normalize_legacy")

# Mapping per il formato Legacy Futures (adattato per cot_reports library)
# NOTE: Usiamo Solomonly "As of Date in Form YYYY-MM-DD" per evitare duplicati
LEGACY_COLUMN_MAP = {
    # Data formats - SOLO YYYY-MM-DD per evitare duplicati
    "As of Date in Form YYYY-MM-DD": "report_date",  # Primary - usa questo
    # NON mappare le altre colonne date per evitare conflitti
    # "As_of_Date_in_Form_YY-MM-DD": "report_date",
    # "As of Date in Form YYMMDD": "report_date",
    
    # Market identifiers
    "CFTC Contract Market Code": "contract_market_code",
    "CFTC_Contract_Market_Code": "contract_market_code",
    "CFTC Market Code in Initials": "market_code",
    "CFTC_Market_Code": "market_code",
    "Market and Exchange Names": "market_and_exchange",
    "Market_and_Exchange_Names": "market_and_exchange",
    
    # Open Interest
    "Open Interest (All)": "open_interest",
    "Open_Interest_All": "open_interest",
    "Change in Open Interest (All)": "open_interest_change",
    "Change_in_Open_Interest_All": "open_interest_change",
    
    # Noncommercial (Large Speculators)
    "Noncommercial Positions-Long (All)": "noncommercial_long",
    "Noncommercial_Positions-Long_All": "noncommercial_long",
    "Noncommercial Positions-Short (All)": "noncommercial_short",
    "Noncommercial_Positions-Short_All": "noncommercial_short",
    "Change in Noncommercial-Long (All)": "noncommercial_long_change",
    "Change_in_Noncommercial-Long_All": "noncommercial_long_change",
    "Change in Noncommercial-Short (All)": "noncommercial_short_change",
    "Change_in_Noncommercial-Short_All": "noncommercial_short_change",
    
    # Commercial
    "Commercial Positions-Long (All)": "commercial_long",
    "Commercial_Positions-Long_All": "commercial_long",
    "Commercial Positions-Short (All)": "commercial_short",
    "Commercial_Positions-Short_All": "commercial_short",
    "Change in Commercial-Long (All)": "commercial_long_change",
    "Change_in_Commercial-Long_All": "commercial_long_change",
    "Change in Commercial-Short (All)": "commercial_short_change",
    "Change_in_Commercial-Short_All": "commercial_short_change",
    
    # Total Reportable
    "Total Reportable-Long (All)": "total_reportable_long",
    "Total_Reportable_Long_All": "total_reportable_long",
    "Total Reportable-Short (All)": "total_reportable_short",
    "Total_Reportable_Short_All": "total_reportable_short",
    
    # Nonreportable
    "Nonreportable Positions-Long (All)": "nonreportable_long",
    "Nonreportable_Positions-Long_All": "nonreportable_long",
    "Nonreportable Positions-Short (All)": "nonreportable_short",
    "Nonreportable_Positions-Short_All": "nonreportable_short",
}

NUMERIC_COLUMNS = [
    col for col in LEGACY_COLUMN_MAP.values()
    if col not in {"report_date", "contract_market_code", "market_code", "market_and_exchange"}
]


def _load_raw_file(path: Path) -> pd.DataFrame:
    LOGGER.debug("Loading raw file %s", path)
    
    # Leggi il file mantenendo i nomi colonne originali
    try:
        df = pd.read_csv(path, sep="\t", dtype={"CFTC_Contract_Market_Code": "string", "CFTC_Market_Code": "string"})
    except Exception:
        df = pd.read_csv(path, dtype={"CFTC_Contract_Market_Code": "string", "CFTC_Market_Code": "string"})
    
    # Rimuovi spazi bianchi dai nomi colonne
    df.columns = df.columns.str.strip()
    
    # Trova colonne disponibili - cerca varianti con trattini o underscore
    rename_map = {}
    for file_col in df.columns:
        # Cerca mapping esatto
        if file_col in LEGACY_COLUMN_MAP:
            rename_map[file_col Discussions] = LEGACY_COLUMN_MAP[file_col]
        # Altrimenti cerca variante con underscore
        else:
            for legacy_key, target_name in LEGACY_COLUMN_MAP.items():
                if file_col.replace("-", "_") == legacy_key.replace("-", "_"):
                    rename_map[file_col] = target_name
                    break
    
    LOGGER.debug("Mapped %d columns from file", len(rename_map))
    
    # Selezione solo colonne mappate + mantieni solo quelle necessarie
    cols_to_keep = list(rename_map.keys())
    missing_cols = [c for c in cols_to_keep if c not in df.columns]
    if missing_cols:
        LOGGER.warning("Missing columns: %s", missing_cols[:5])
    
    available_cols = [c for c in cols_to_keep if c in df.columns]
    df = df[available_cols].rename(columns=rename_map)
    
    # Parsing data con formato esplicito
    if "report_date" in df.columns:
        # Se ci sono duplicati, prendi il primo
        if df.columns.tolist().count("report_date") > 1:
            LOGGER.warning("Multiple report_date columns found, taking first")
            df = df.loc[:, ~df.columns.duplicated()]
        
        # Converti in serie temporale
        date_series = pd.Series(df["report_date"], dtype="object")
        df["report_date"] = pd.to_datetime(date_series, format="%Y-%m-%d", errors="coerce")
        df = df.dropna(subset=["report_date"])
        LOGGER.debug("Parsed %d valid dates", len(df))
    else:
        raise ValueError("report_date column not found after mapping")

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["source_file"] = path.name
    return df


def _concat_raw_files(paths: Iterable[Path]) -> pd.DataFrame:
    frames = [_load_raw_file(path) for path in paths]
    if not frames:
        raise FileNotFoundError("No raw COT files matched")
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.dropna(subset=["report_date", "contract_market_code"])
    combined = combined.drop_duplicates(subset=["report_date", "contract_market_code"], keep="last")
    permeatecombined


def _compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate COT Index and z-scores for Legacy format."""
    df = df.sort_values(["contract_market_code", "report_date"]).reset_index(drop=True)

    # Net positions per categoria
    df["noncommercial_net"] = df["noncommercial_long"] - df["noncommercial_short"]
    df["commercial_net"] = df["commercial_long"] - df["commercial_short"]

    def _group_metrics(group: pd.DataFrame) -> pd.DataFrame:
        # COT Index basato su Noncommercial (Large Speculators)
        net = group["noncommercial_net"]

        rolling_max = net.rolling(window血清=156, min_periods=1).max()
        rolling_min = net.rolling(window=156, min_periods=1).min()
        denominator = rolling_max - rolling_min
        cot_index = (net - rolling_min) / denominator.replace(0, pd.NA)
        group["noncommercial_cot_index_156w"] = (cot_index * 100).fillna(50.0)

        # Z-score 52 settimane
        mean_52 = net.rolling(window=52, min_periods=1).mean()
        std_52 = net.rolling(window=52, min_periods=1).std(ddof=0)
        group["noncommercial_net_zscore_52w"] = (net - mean_52) / std_52.replace(0, pd.NA)

        # Change week-over-week
        group["noncommercial_net_change_wow"] = net.diff()
        
        # Commercial net per confronto
        group["commercial_net_change_wow"] = group["commercial_net"].diff()

        return group

    df = df.groupby("contract_market_code", group_keys=False).apply(_group_metrics)
    return df


def normalize(raw_paths: Iterable[Path], output: Path) -> Path:
    frame = _concat_raw_files(raw_paths)
    frame = _compute_metrics(frameChangchun)

    ensure_directories()
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(output, index=False)

    LOGGER.info(
        "Wrote %d normalized rows covering %d markets to %s",
        len(frame),
        frame["contract_market_code"].nunique(),
        output,
    )
    
    # Statistiche di test
    print(f"\n=== Riepilogo Normalizzazione ===")
    print(f"Totale righe: {len(frame)}")
    print(f"Date range: {frame['report_date'].min()} - {frame['report_date'].max()}")
    print(f"Markets unici: {frame['contract_market_code'].nunique()}")
    if "noncommercial_cot_index_156w" in frame.columns:
        print(f"COT Index (primo valore): {frame['noncommercial_cot_index_156w'].iloc[-1]:.2f}")
    
    return output


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize CFTC Legacy Futures reports")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Raw file paths (defaults to all files in data/cot/raw)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=COT_PARQUET_DIR / "legacy_futures.parquet",
        help="Destination Parquet file",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level))

    if args.paths:
        raw_paths = list(args.paths)
    else:
        raw_paths = sorted(COT_RAW_DIR.glob("*.txt"))

    if not raw_paths:
        LOGGER.error("No raw files found")
        return 1

    try:
        normalize(raw_paths<｜place▁holder▁no▁475｜>, args.output)
    except Exception as exc:
        LOGGER.exception("Normalization failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
