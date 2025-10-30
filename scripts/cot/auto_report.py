# -*- coding: utf-8 -*-
"""Report automatico COT per Team Command Cursor."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Fix encoding UTF-8 per Windows e importa utility avanzate
from shared.encoding_utils import force_utf8_stdout, safe_print, sanitize_ascii, format_number_ascii
force_utf8_stdout()

import duckdb
from shared.config import COT_DUCKDB_PATH

# Path per salvare report in file UTF-8 (per copia/incolla affidabile)
REPORTS_DIR = REPO_ROOT / "data" / "reports"
REPORT_UTF8_FILE = REPORTS_DIR / "cot_report_utf8.txt"

# Mapping strumenti -> market codes COT
INSTRUMENTS = {
    "AUD": ("232741", "AUSTRALIAN DOLLAR"),
    "GBP": ("096742", "BRITISH POUND"),
    "CAD": ("090741", "CANADIAN DOLLAR"),
    "EUR": ("099741", "EURO FX"),
    "JPY": ("097741", "JAPANESE YEN"),
    "CHF": ("092741", "SWISS FRANC"),
    "NZD": ("112741", "NZ DOLLAR"),
    "S&P 500": None,  # Da cercare
    "NASDAQ": None,  # Da cercare
    "Russell 2000": ("239742", "RUSSELL E-MINI"),
    "E-MINI S&P 500": None,  # Da cercare
    "VIX": None,  # Da cercare
    "GOLD": None,  # Da cercare
    "SILVER": None,  # Da cercare
}


def find_market_codes(con: duckdb.DuckDBPyConnection):
    """Trova market codes mancanti cercando nel database."""
    # Query per trovare strumenti simili
    # IMPORTANTE: ordine conta - pattern più specifici PRIMA
    queries = [
        ("E-MINI S&P 500", "%E-MINI S&P 500%", None),
        ("S&P 500", "%S&P 500%", "%E-MINI%"),  # Esclude E-MINI
        ("NASDAQ", "%NASDAQ-100%", None),
        ("VIX", "%VIX FUTURES%", None),
        ("GOLD", "%GOLD%", None),
        ("SILVER", "%SILVER%", None),
    ]
    
    found = {}
    for query_item in queries:
        name, pattern, exclude_pattern = query_item
        
        if exclude_pattern:
            sql = """
                SELECT DISTINCT contract_market_code, market_and_exchange 
                FROM cot_disagg 
                WHERE market_and_exchange LIKE ? 
                  AND market_and_exchange NOT LIKE ?
                ORDER BY market_and_exchange
                LIMIT 1
            """
            result = con.execute(sql, [pattern, exclude_pattern]).fetchone()
        else:
            sql = """
                SELECT DISTINCT contract_market_code, market_and_exchange 
                FROM cot_disagg 
                WHERE market_and_exchange LIKE ?
                ORDER BY market_and_exchange
                LIMIT 1
            """
            result = con.execute(sql, [pattern]).fetchone()
        
        if result:
            found[name] = result[0]
    
    return found


def get_latest_date(con: duckdb.DuckDBPyConnection) -> str:
    """Trova ultima data disponibile."""
    result = con.execute("SELECT MAX(report_date) FROM cot_disagg").fetchone()[0]
    return result.strftime("%Y-%m-%d") if result else None


def get_instrument_data(con: duckdb.DuckDBPyConnection, code: str, date: str):
    """Estrae dati COT per uno strumento."""
    result = con.execute("""
        SELECT noncommercial_long, noncommercial_short, 
               noncommercial_long_change, noncommercial_short_change
        FROM cot_disagg 
        WHERE contract_market_code = ? AND report_date = ?
    """, [code, date]).fetchone()
    
    if result:
        long_pos, short_pos, delta_long, delta_short = result
        
        # Gestione valori None/NaN esplicita
        import math
        def is_nan_or_none(val):
            return val is None or (isinstance(val, float) and math.isnan(val))
        
        if is_nan_or_none(long_pos):
            long_pos = 0.0
        if is_nan_or_none(short_pos):
            short_pos = 0.0
        if is_nan_or_none(delta_long):
            delta_long = 0.0
        if is_nan_or_none(delta_short):
            delta_short = 0.0
        
        bias_total = float(long_pos) - float(short_pos)
        bias_delta = float(delta_long) - float(delta_short)
        
        return {
            "long_total": int(long_pos),
            "short_total": int(short_pos),
            "delta_long": int(delta_long),
            "delta_short": int(delta_short),
            "delta_week": int(bias_delta),
            "bias_open": int(bias_total),
            "available": True
        }
    return {"available": False}


def generate_report():
    """Genera report completo."""
    # Pulisci file report precedente (overwrite mode)
    if REPORT_UTF8_FILE.exists():
        REPORT_UTF8_FILE.unlink()
    
    con = duckdb.connect(str(COT_DUCKDB_PATH))
    
    try:
        # Trova ultima data
        latest_date = get_latest_date(con)
        if not latest_date:
            safe_print("No data available", ascii_only=True)
            return
        
        # Trova market codes manc.canti
        found_codes = find_market_codes(con)
        
        # Completa mapping
        instruments_map = {}
        for name, code_info in INSTRUMENTS.items():
            if code_info is None:
                if name in found_codes:
                    instruments_map[name] = found_codes[name]
                else:
                    instruments_map[name] = None
            else:
                instruments_map[name] = code_info[0]
        
        # Header report
        header_line = f"{latest_date} (ultimo report disponibile)\n"
        safe_print(
            header_line,
            ascii_only=True,
            tee_file_utf8=str(REPORT_UTF8_FILE)
        )
        
        # Query per ogni strumento
        results = {}
        for name, code in instruments_map.items():
            if code:
                data = get_instrument_data(con, code, latest_date)
                if data["available"]:
                    # Format bias description
                    if abs(data["bias_open"]) > 50000:
                        bias_desc = f"(forte {'long' if data['bias_open'] > 0 else 'short'})"
                    elif abs(data["bias_open"]) > 10000:
                        bias_desc = f"(strong {'long' if data['bias_open'] > 0 else 'short'})"
                    else:
                        bias_desc = "(allineato)"
                    
                    # Format output senza separatori delle migliaia (tutti attaccati)
                    delta_sign = "+" if data["delta_week"] >= 0 else ""
                    bias_sign = "+" if data["bias_open"] >= 0 else ""
                    
                    delta_long_str = f"+{data['delta_long']}" if data['delta_long'] >= 0 else str(data['delta_long'])
                    delta_short_str = f"+{data['delta_short']}" if data['delta_short'] >= 0 else str(data['delta_short'])
                    
                    # Formatta numeri senza virgole (tutti attaccati)
                    delta_week_fmt = str(data['delta_week'])
                    bias_open_fmt = str(data['bias_open'])
                    long_total_fmt = str(data['long_total'])
                    short_total_fmt = str(data['short_total'])
                    
                    # Usa il nome originale (non sanitizzato) per il file UTF-8
                    # La sanitizzazione avviene solo per la console
                    line = (
                        f"{name}: DELTA settimana {delta_sign}{delta_week_fmt} "
                        f"(Long: {delta_long_str}, Short: {delta_short_str}); "
                        f"BIAS aperto {bias_sign}{bias_open_fmt} "
                        f"(Long: {long_total_fmt}, Short: {short_total_fmt}) {bias_desc}"
                    )
                    
                    # Stampa in console (ASCII) e scrivi in file (UTF-8 originale)
                    safe_print(
                        line,
                        ascii_only=True,  # Console ASCII pulita
                        tee_file_utf8=str(REPORT_UTF8_FILE)  # File UTF-8 per copia/incolla
                    )
                    
                    results[name] = data
                else:
                    results[name] = None
        
        return results
    finally:
        con.close()


if __name__ == "__main__":
    generate_report()