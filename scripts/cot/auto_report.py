# -*- coding: utf-8 -*-
"""Report automatico COT per Team Command Cursor."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Fix encoding UTF-8 per Windows
from shared.encoding_fix import setup_utf8_encoding
setup_utf8_encoding()

import duckdb
from shared.config import COT_DUCKDB_PATH


def safe_print(*args, **kwargs):
    """Print sicuro che forza UTF-8 encoding anche su terminali Windows problematici."""
    try:
        # Converte argomenti in stringa
        text = ' '.join(str(arg) for arg in args)
        if kwargs.get('end', '\n') != '':
            text += kwargs.get('end', '\n')
        
        # Scrive direttamente nel buffer con encoding UTF-8 esplicito
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout.buffer.write(text.encode('utf-8', errors='replace'))
            sys.stdout.buffer.flush()
        else:
            # Fallback se buffer non disponibile
            print(*args, **kwargs)
    except Exception:
        # Fallback: usa print normale
        try:
            print(*args, **kwargs)
        except Exception:
            pass  # Ignora errori di encoding estremi

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
    queries = [
        ("S&P 500", "%S&P%"),
        ("NASDAQ", "%NASDAQ%"),
        ("E-MINI S&P 500", "%E-MINI%S&P%"),
        ("VIX", "%VIX%"),
        ("GOLD", "%GOLD%"),
        ("SILVER", "%SILVER%"),
    ]
    
    found = {}
    for name, pattern in queries:
        result = con.execute("""
            SELECT DISTINCT contract_market_code, market_and_exchange 
            FROM cot_disagg 
            WHERE market_and_exchange LIKE ?
            LIMIT 1
        """, [pattern]).fetchone()
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
    con = duckdb.connect(str(COT_DUCKDB_PATH))
    
    try:
        # Trova ultima data
        latest_date = get_latest_date(con)
        if not latest_date:
            safe_print("No data available")
            return
        
        # Trova market codes mancanti
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
        
        safe_print(f"{latest_date} (ultimo report disponibile)\n")
        
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
                    
                    # Format output
                    delta_sign = "+" if data["delta_week"] >= 0 else ""
                    bias_sign = "+" if data["bias_open"] >= 0 else ""
                    
                    delta_long_str = f"+{data['delta_long']}" if data['delta_long'] >= 0 else str(data['delta_long'])
                    delta_short_str = f"+{data['delta_short']}" if data['delta_short'] >= 0 else str(data['delta_short'])
                    
                    safe_print(f"{name}: DELTA settimana {delta_sign}{data['delta_week']:,} "
                          f"(Long: {delta_long_str}, Short: {delta_short_str}); "
                          f"BIAS aperto {bias_sign}{data['bias_open']:,} "
                          f"(Long: {data['long_total']:,}, Short: {data['short_total']:,}) {bias_desc}")
                    
                    results[name] = data
                else:
                    results[name] = None
        
        return results
    finally:
        con.close()


if __name__ == "__main__":
    generate_report()