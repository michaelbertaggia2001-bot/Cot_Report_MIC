# COT Reports Pipeline

Pipeline completa per scaricare, normalizzare e analizzare i report COT (Commitments of Traders) ufficiali CFTC.

## Caratteristiche

- ✅ Download automatico dei dati COT più recenti
- ✅ Conversione CSV→Parquet ottimizzata (idempotente)
- ✅ Database DuckDB per query performanti
- ✅ Report automatici per strumenti principali
- ✅ Comandi Cursor integrati per uso rapido

## Installazione

### Requisiti

Python 3.8+ richiesto.

### Dipendenze

```bash
pip install cot-reports pandas duckdb pyarrow
```

**Dipendenze principali:**
- `cot-reports`: Download dati COT da CFTC
- `pandas`: Manipolazione dati
- `duckdb`: Database SQL per analisi veloci
- `pyarrow`: Supporto formato Parquet

### Setup Iniziale (dopo git clone)

**Cosa viene scaricato da GitHub:**
- ✅ Tutto il codice sorgente Python
- ✅ File di configurazione (`shared/config.py`)
- ✅ Comandi Cursor (`.cursor/commands/`)
- ✅ Documentazione (`README.md`)
- ✅ Struttura directory (vuote)

**Cosa NON viene scaricato (escluso da `.gitignore`):**
- ❌ File di dati COT (CSV, Parquet)
- ❌ Database DuckDB (`cot.db`)
- ❌ File temporanei (`annual.txt`, `__pycache__`)
- ❌ Cache IDE

**Perché?** I dati sono esclusi per limitare la dimensione del repository. Ogni utente può scaricare solo i dati necessari quando ne ha bisogno.

**Setup completo:**

```bash
# 1. Installa dipendenze
pip install cot-reports pandas duckdb pyarrow

# 2. Scarica e sincronizza dati (prima volta)
python scripts/cot/update_cot_pipeline.py
```

Questo comando:
- Scarica i dati COT più recenti disponibili online
- Li converte automaticamente in formato Parquet
- Sincronizza tutto nel database DuckDB

**Prima esecuzione:** I dati 2023-2025 verranno scaricati (~100MB totali).

**Esecuzioni successive:** Solo nuovi dati (incrementale).

### Workflow Completo (primo uso su nuovo PC)

```bash
# 1. Clone repository
git clone <repository-url>
cd Cot-Report

# 2. Installa dipendenze
pip install cot-reports pandas duckdb pyarrow

# 3. Scarica dati (prima volta - scarica tutto)
python scripts/cot/update_cot_pipeline.py
# Questo scaricherà: 2023, 2024, 2025 (~100MB, ~2-5 minuti)

# 4. Verifica funzionamento
python scripts/cot/auto_report.py
```

**Nota:** La prima esecuzione di `update_cot_pipeline.py` scaricherà tutti gli anni disponibili se non trova dati locali. Le esecuzioni successive scaricano solo i nuovi dati settimanali.

### Setup Alternativo (se hai già i file Parquet)

Se hai già i file Parquet da un'altra fonte o backup:

```bash
# 1. Copia i file Parquet in data/cot/parquet/
# es: legacy_futures_2023.parquet, legacy_futures_2024.parquet, etc.

# 2. Sincronizza solo DuckDB (senza scaricare)
python scripts/cot/sync_complete.py
```

Questo script legge tutti i file Parquet presenti in `data/cot/parquet/` e li sincronizza nel database DuckDB.

### Note Importanti

- **File `annual.txt`**: File temporaneo generato dalla libreria `cot_reports` durante il download. Viene automaticamente ignorato da git (`.gitignore`). Puoi eliminarlo manualmente, viene ricreato ad ogni download.
- **Directory vuote**: Le directory `data/cot/csv/` e `data/cot/parquet/` saranno vuote dopo git clone. Gli script le creano automaticamente quando necessario tramite `ensure_directories()`.

## Struttura Progetto

```
Cot Report/
├── shared/
│   └── config.py              # Configurazione centrale
├── scripts/cot/
│   ├── auto_report.py          # Report automaticoopol
│   ├── update_cot_pipeline.py  # Pipeline aggiornamento
│   ├── auto_convert_csv_to_parquet.py  # Converter
│   ├── query.py                # Query utility
│   ├── sync_complete.py        # Sync DuckDB completo
│   └── normalize_legacy_cot.py # Normalizer Legacy format
├── .cursor/commands/
│   ├── analisi_ultima_settimana.md  # Comando report
│   └── update.md                     # Comando update
└── data/
    ├── cot/csv/                # File CSV scaricati
    ├── cot/parquet/            # File Parquet ottimizzatiتح
    └── duckdb/cot.db          # Database DuckDB
```

## Uso Rapido

### Comandi Cursor (raccomandato)

Usa i comandi Cursor integrati:
- `/analisi_ultima_settimana` - Report completo ultimi dati
- `/update` - Aggiorna i dati più recenti

### Script Manuali

#### 1. Aggiorna dati COT
```bash
python scripts/cot/update_cot_pipeline.py
```

#### 2. Genera report automatico
```bash
python scripts/cot/auto_report.py
```

Output esempio:
```
2025-09-23 (ultimo report disponibile)

EUR: DELTA settimana -3414 (Long敌人 -789, Short: +2625); BIAS aperto +114345 (Long: 252472, Short: 138127) (forte long)
JPY: DELTA settimana +18089 (Long: +14727, Short: -3362); BIAS aperto +79500 (Long: 176400, Short: 96900) (forte long)
...
```

#### 3. Query personalizzate
```bash
python scripts/cot/query.py "SELECT * FROM cot_disagg WHERE contract_market_code =思维方式 '099741' AND report_date = '2025-09-23'"
```

## Dataset

- **Periodo**: 2023-2025 (~143 settimane)
- **Markets**: ~400 mercati diversi
- **Formato**: Legacy Futures Only (CFTC)
- **Metriche**: COT Index 156w, Z-score 52w, Week-over-week changes

## Market Codes Principali

- **EUR FX**: 099741
- **Japanese Yen**: 097741
- **Canadian Dollar**: 090741
- **British Pound**: 096742
- **Swiss Franc**: 092741
- **Australian Dollar**: 232741
- **NZ Dollar**: 112741
- **VIX**: 1170E1
- **Gold**: 088691
- **Silver**: 084691

## Pipeline Completa

1. **Download** → Script scarica dati anno corrente via `cot_reports`
2. **Convert** → CSV→Parquet automatico (solo se necessario)
3. **Sync** → Aggiorna DuckDB con nuovi dati
4. **Query** → Interroga database per analisi

Tutti i passaggi sono idempotenti e automatici.

## Performance

- Parquet: **10x più piccolo** di CSV
- Query DuckDB: **100x più veloci** rispetto a file flat
- Compressione automatica
- Schema typed (date, int, float nativi)

## File Temporanei

### annual.txt

File temporaneo generato dalla libreria `cot_reports` durante il download dei dati. 
- **Cos'è**: File intermedio che la libreria crea nella working directory
- **Dove**: Root del progetto (o directory corrente quando viene eseguito lo script)
- **Perché esiste**: Comportamento interno della libreria `cot_reports`
- **Cosa fare**: Puoi ignorarlo o eliminarlo. Viene automaticamente escluso da git tramite `.gitignore`
- **Quando**: Appare durante l'esecuzione di `update_cot_pipeline.py` quando viene scaricato un nuovo anno

## .gitkeep - Spiegazione

### Cosa fa `.gitkeep`?

File `.gitkeep` è una convenzione Git per mantenere directory vuote nel repository. Git di default non committa directory vuote.

**Vantaggi:**
- ✅ Mantiene la struttura directory nel repository
- ✅ Evita errori se script si aspettano directory esistenti
- ✅ Chiara documentazione della struttura del progetto

**Svantaggi:**
- ⚠️ File "fantasma" che non ha contenuto reale
- ⚠️ La directory viene comunque creata automaticamente dagli script (`ensure_directories()`)

**Decisione per questo progetto:**
Gli script già creano automaticamente le directory se non esistono tramite `ensure_directories()`, quindi `.gitkeep` non è strettamente necessario. Se preferisci una struttura più pulita, puoi ometterli - gli script funzioneranno comunque.

## Troubleshooting

### Errore: "No module named 'cot_reports'"
```bash
pip install cot-reports
```

### Errore: "No data available"
Esegui prima:
```bash
python scripts/cot/update_cot_pipeline.py
```

### Errore: "FileNotFoundError: cot.db"
Il database viene creato automaticamente. Se persiste, verifica i permessi di scrittura nella directory `data/duckdb/`.

## Licenza

[Specificare licenza se applicabile]