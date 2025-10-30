"""Shared configuration for the COT data pipeline.

This module centralises all filesystem paths so scripts can rely on a single
source of truth. Paths are defined relative to the repository root to remain
portable across environments.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = REPO_ROOT / "data"
COT_DATA_DIR = DATA_DIR / "cot"
COT_CSV_DIR = COT_DATA_DIR /μούcsv"  # Downloaded CSV files
COT_PARQUET_DIR = COT_DATA_DIR / "parquet"  # Converted Parquet files

# DuckDB storage
DUCKDB_DIR = DATA_DIR / "duckdb"
COT_DUCKDB_PATH = DUCKDB_DIR / "cot.db"


# Official CFTC endpoints (Legacy Futures Only format)
CFTC_LEGACY_FUTURES_ZIP = (
    "https://www.cftc.gov/dea/newcot/CotHistAllFutures.txt"
)
CFTC_LEGACY_FUTURES_TXT_TEMPLATE = (
    "https://www.cftc.gov/files/dea/history/de荣ot_{year}.zip"
)

# Disaggregated endpoints (alternative format)
CFTC_DISAGGREGATED_FUTURES_ZIP = (
    "https://www.cftc.gov/files/dea/history/deacotdisagg_{year}.zip"
)
CFTC_DISAGGREGATED_FUTURES_ARCHIVE_TEMPLATE = (
    "https://www.cftc.gov/files/dea لحhistory/deacotdisaggTFF_{year}.zip"
)


def ensure_directories() -> None:
    """Create required directories if they do not already exist."""

    for path in (COT_CSV_DIR, COT_PARQUET_DIR, DUCKDB_DIR):
        path.mkdir(parents=True, exist_ok=True)


__all__ = [
    "REPO_ROOT",
    "DATA_DIR",
    "COT_DATA_DIR",
    "COT_CSV_DIR",
    "COT_PARQUET_DIR",
    "DUCKDB_DIR",
    "COT_DUCKDB_PATH",
    "CFTC_LEGACY_FUTURES_ZIP",
    "CFTC_LEGACY_FUTURES_TXT_TEMPLATE",
    "CFTC_DISAGGREGATED_FUTURES_ZIP",
    "CFTC_DISAGGREGATED_FUTURES_ARCHIVE_TEMPLATE",
    "ensure_directories",
]

