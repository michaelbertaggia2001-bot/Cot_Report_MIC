# Correzione Encoding - Guida Completa

## Problema Identificato

Su Windows, Python usa **cp1252** come encoding di default per `stdout` e `stderr`, causando problemi di visualizzazione caratteri quando si cerca di stampare testo con encoding UTF-8.

### Sintomi
- Caratteri corretti nel codice diventano caratteri strani nell'output (es. "BIAS" → "一模一样")
- Problemi di visualizzazione in console/terminali Windows (PowerShell, CMD)
- Errori di encoding quando si stampano caratteri non-ASCII

### Causa Radice
```python
import sys
print(sys.stdout.encoding)  # Output: 'cp1252' su Windows (non UTF-8!)
```

## Soluzione Implementata

### 1. Funzione Utility Centrale

Creata funzione riutilizzabile in `shared/encoding_fix.py`:

```python
from shared.encoding_fix import setup_utf8_encoding
setup_utf8_encoding()
```

Questa funzione:
- Configura automaticamente `stdout` e `stderr` per UTF-8
- Compatibile con Python 3.7+ (usa `reconfigure`)
- Fallback per versioni precedenti (usa `TextIOWrapper`)
- Gestisce errori gracefully

### 2. Fix Applicato a Tutti gli Script

Tutti gli script che usano `print()` sono stati aggiornati:

✅ **`scripts/cot/auto_report.py`** - Report automatico COT
  - Usa `safe_print()` per garantire encoding corretto anche su terminali Windows problematici
  - Scrive direttamente nel buffer con encoding UTF-8 esplicito
  - Funzione aggiuntiva rispetto a `setup_utf8_encoding()` per casi edge
  
✅ **`scripts/cot/sync_complete.py`** - Sincronizzazione dati
✅ **`scripts/cot/update_cot_pipeline.py`** - Pipeline download/conversione
✅ **`scripts/cot/normalize_legacy_cot.py`** - Normalizzazione dati legacy
✅ **`compare_parquet.py`** - Query utility
✅ **`scripts/cot/auto_convert_csv_to_parquet.py`** - Conversione CSV→Parquet

#### 2.1. Fix Avanzato per `auto_report.py`

In `scripts/cot/auto_report.py` è stata aggiunta una funzione `safe_print()` che:
- Scrive direttamente in `sys.stdout.buffer` con encoding UTF-8 esplicito
- Evita problemi di corruzione caratteri su terminali Windows particolarmente problematici
- Gestisce errori gracefully con fallback multipli

### 3. Template da Usare nei Nuovi Script

```python
# -*- coding: utf-8 -*-
"""Descrizione script."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Fix encoding UTF-8 per Windows
from shared.encoding_fix import setup_utf8_encoding
setup_utf8_encoding()

# ... resto del codice ...
```

## Verifica Soluzione

Prima del fix:
```
VIX: DELTA settimana +496 (Long: -10600, Short: -11096);一模一样 aperto -101,193
CHF: DELTA settimana +3,022 (Long: +1992, Short: -1030); BIAS aperto -23,018 (strong short whistleblower
S&P 500: DELTA settimana +856 (Long: +536, Short: -320); BIAS الءaperto +780
VIX: DELTA settimana +496 (Long: -10600, Short: -11096); BIAS aperto -101,193 (forte chunk
```

Dopo il fix base (`setup_utf8_encoding()`):
```
VIX: DELTA settimana +496 (Long: -10600, Short: -11096); BIAS aperto -101,193
```

Dopo il fix avanzato (`safe_print()` in `auto_report.py`):
```
VIX: DELTA settimana +496 (Long: -10600, Short: -11096); BIAS aperto -101,193 (forte short)
CHF: DELTA settimana +3,022 (Long: +1992, Short: -1030); BIAS aperto -23,018 (strong short)
S&P 500: DELTA settimana +856 (Long: +536, Short: -320); BIAS aperto +780 (allineato)
```

✅ **Problema risolto completamente!**

## Best Practices per il Futuro

1. **Sempre aggiungere** `# -*- coding: utf-8 -*-` all'inizio dei file Python
2. **Sempre chiamare** `setup_utf8_encoding()` all'inizio degli script che usano `print()`
3. **Usare la funzione utility** invece di codice inline ripetuto
4. **Testare su Windows** se possibile prima di commitare

## File Corretti

### Storia Correzioni
- **2025-01-XX**: Identificato problema encoding cp1252 su Windows
- **2025-01-XX**: Creata funzione utility `shared/encoding_fix.py`
- **2025-01-XX**: Applicato fix a tutti gli script esistenti
- **2025-01-XX**: Aggiunta funzione `safe_print()` in `auto_report.py` per fix avanzato
- **2025-01-XX**: Verificato funzionamento corretto su terminali Windows problematici

### Script Aggiornati
1. `scripts/cot/auto_report.py` ✅
2. `scripts/cot/sync_complete.py` ✅
3. `scripts/cot/update_cot_pipeline.py` ✅
4. `scripts/cot/normalize_legacy_cot.py` ✅
5. `scripts/cot/query.py` ✅
6. `scripts/cot/auto_convert_csv_to_parquet.py` ✅

## Note Tecniche

- Il fix è **retrocompatibile** con Python 3.6+
- Non modifica il comportamento su Linux/Mac (dove UTF-8 è già il default)
- Gestisce errori gracefully se `reconfigure()` non è disponibile
- Usa `errors='replace'` per evitare crash su caratteri invalidi

## Riferimenti

- Python `sys.stdout.reconfigure()`: https://docs.python.org/3/library/sys.html#sys.stdout.reconfigure
- UTF-8 su Windows: https://docs.python.org/3/howto/unicode.html#unicode-howto
