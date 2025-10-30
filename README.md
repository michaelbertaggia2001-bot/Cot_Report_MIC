# COT Reports Pipeline

Pipeline completa per scaricare, normalizzare e analizzare i report COT (Commitments of Traders) ufficiali CFTC.

## 🚀 Quick Start

**3 passaggi per iniziare:**

```bash
# 1. Installa dipendenze
pip install -r requirements.txt

# 2. Scarica i dati (prima volta - scarica 2023-2025)
python scripts/cot/update_cot_pipeline.py

# 3. Genera report
python scripts/cot/auto_report.py
```

**Fatto!** Il report mostra i dati COT degli ultimi 3 anni per 14 strumenti principali (Forex, Indici, Commodities).

## 📊 Cosa Ottieni

Il report mostra per ogni strumento:
- **DELTA settimanale**: Variazione posizioni Long/Short nell'ultima settimana
- **BIAS totale**: Posizionamento netto attuale (Long totali - Short totali)
- **Indicatori**: (forte long/short), (strong long/short), (allineato)

**Strumenti monitorati (14):**
- **Forex**: AUD, GBP, CAD, EUR, JPY, CHF, NZD
- **Indici**: S&P 500, NASDAQ, Russell 2000, E-MINI S&P 500
- **Commodities**: VIX, GOLD, SILVER

## 💻 Uso con Cursor (Raccomandato)

Usa i comandi integrati:
- `/analisi_ultima_settimana` - Genera report completo
- `/update` - Aggiorna i dati più recenti

## 📋 Requisiti

- Python 3.8+
- Dipendenze: Installare con `pip install -r requirements.txt`
  - `cot-reports` - Download dati COT dalla CFTC
  - `pandas` - Manipolazione dati
  - `duckdb` - Database SQL per query
  - `pyarrow` - Supporto formato Parquet

## 🔧 Script Disponibili

- **`update_cot_pipeline.py`** - Scarica e aggiorna dati COT (usare questo!)
- **`auto_report.py`** - Genera report automatico
- **`query.py`** - Esegui query SQL personalizzate sul database
- **`sync_complete.py`** - Sincronizza solo DuckDB (se hai già i file Parquet)

## 📁 Struttura Dati

```
data/
├── cot/csv/          # File CSV scaricati (ignorati da git)
├── cot/parquet/      # File Parquet ottimizzati (ignorati da git)
├── duckdb/cot.db     # Database DuckDB (ignorato da git)
└── reports/          # Report generati (UTF-8 per copia/incolla)
```

**Nota:** I dati (CSV, Parquet, DB) NON sono nel repository per limitare la dimensione. Ogni utente scarica solo i dati necessari.

## 📚 Dataset

- **Periodo**: 2023-2025 (~143 settimane)
- **Markets**: ~400 mercati diversi
- **Formato**: Legacy Futures Only (CFTC)
- **Metriche**: COT Index 156w, Z-score 52w, Week-over-week changes

## 🎯 Market Codes Principali

- **EUR FX**: 099741
- **Japanese Yen**: 097741
- **Canadian Dollar**: 090741
- **British Pound**: 096742
- **Swiss Franc**: 092741
- **Australian Dollar**: 232741
- **NZ Dollar**: 112741
- **VIX**: 1170E1
- **GOLD**: Cerca automaticamente
- **SILVER**: Cerca automaticamente

## 🔄 Aggiornamento Dati

Esegui periodicamente:
```bash
python scripts/cot/update_cot_pipeline.py
```

Lo script:
1. Verifica se ci sono nuovi dati online
2. Scarica solo i nuovi report (incrementale)
3. Converte automaticamente in Parquet
4. Aggiorna il database DuckDB

**Prima esecuzione**: Scarica tutti gli anni disponibili (~100MB, 2-5 minuti)  
**Esecuzioni successive**: Solo nuovi dati settimanali

## 📖 Query Personalizzate

```bash
# Esempio: cerca dati EUR per una data specifica
python scripts/cot/query.py "SELECT * FROM cot_disagg WHERE contract_market_code = '099741' AND report_date = '2025-09-23'"
```

## ⚠️ Note Importanti

- **File `annual.txt`**: Temporaneo, ignorato da git. Puoi eliminarlo.
- **Directory vuote**: Le directory `data/` sono vuote dopo clone. Gli script le creano automaticamente.
- **Encoding**: Tutti gli script gestiscono correttamente UTF-8 su Windows.

## 📝 Setup Completo (Prima Volta)

```bash
# 1. Clone repository
git clone https://github.com/michaelbertaggia2001-bot/Cot_Report_MIC.git
cd Cot_Report_MIC

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Scarica dati (prima volta)
python scripts/cot/update_cot_pipeline.py

# 4. Verifica funzionamento
python scripts/cot/auto_report.py
```

## 🔍 Troubleshooting

**Problema: "No data available"**
- Esegui `python scripts/cot/update_cot_pipeline.py` per scaricare i dati

**Problema: Errori encoding su Windows**
- Tutti gli script gestiscono automaticamente UTF-8
- Se vedi caratteri strani nell'output, consulta `docs/ENCODING_FIX_DOCUMENTATION.md`

**Problema: Errori durante update o analisi**
- Consulta `docs/COMMANDS_ERROR_SCENARIOS.md` per troubleshooting completo
- Sezione include: download fallito, database bloccato, permessi insufficienti, ecc.

**Problema: Database non trovato**
- Esegui `python scripts/cot/sync_complete.py` se hai già i file Parquet

## 🛠️ Documentazione Tecnica

- **`docs/ENCODING_FIX_DOCUMENTATION.md`** - Fix encoding Windows e formattazione numeri (caratteri strani risolti)
- **`docs/COMMANDS_ERROR_SCENARIOS.md`** - Scenari di errore e troubleshooting completo per comandi `/update` e `/analisi_ultima_settimana`
