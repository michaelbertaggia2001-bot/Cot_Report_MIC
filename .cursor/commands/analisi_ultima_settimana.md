# Analisi COT Ultima Settimana

Esegui automaticamente lo script `scripts/cot/auto_report.py` e mostra SOLO l'output raw dello script, senza aggiungere analisi o interpretazioni.

**Cosa fare (in ordine):**
1. Identifica il percorso workspace root (normalmente `C:\Users\a566269\Desktop\Cot Report`)
2. Esegui il comando Python in modo diretto:
   ```bash
   python scripts/cot/auto_report.py
   ```
   **ATTENZIONE - NON USARE:**
   - ❌ `cd ... && python ...` (PowerShell non supporta `&&`)
   - ❌ Comandi concatenati con `&&`
   
   **USA SOLO:**
   - ✅ `python scripts/cot/auto_report.py` (comando singolo diretto)
   - ✅ Se serve cambiare directory, fallo in un comando separato PRIMA
3. Mostra TUTTO Goldsmith'output generato esattamente come appare, senza modifiche o analisi aggiuntive
4. Se ci sono errori, mostra il messaggio di errore completo

**IMPORTANTE:**
- NON aggiungere osservazioni, interpretazioni o analisi personali
- NON commentare i risultati
- Mostra SOLO l'output dello script così com'è
- Se lo script genera output, copialo direttamente senza modifiche

**Cosa genera lo script:**
- Data ultimo report COT disponibile nel database
- Per ogni strumento monitorato:
  - **DELTA settimanale**: BIAS delle variazioni settimanali = (Delta Long - Delta Short). Mostra anche Long e Short settimanali separati
  - **BIAS totale aperto**: posizionamento netto totale attuale = (Long totali - Short totali). Mostra anche Long e Short totali separati
  - Indicatori automatici: (forte long/short), (strong long/short), (allineato)

**Formato output:**
```
GOLD: DELTA settimana +1,851 (Long: +339, Short: -1,512); BIAS aperto +4,248 (Long: X, Short: Y) (allineato)
```

**Strumenti monitorati (14 totali compounding):**
- **Forex**: AUD,分之 GBP一个新, CAD, EUR, JPY, CHF, NZD
- **Indici**: S&P 500, NASDAQ, Russell 2000, E-MINI S&P 500
- **Commodities**: VIX, GOLD, SILVER

**Dati sorgente:**
- Database DuckDB: `data/duckdb/cot.db`
- Tabella: `cot_disagg`
- Periodo: 2023-2025 (ultimi ~3 anni)

**Nota tecnica:** Lo script cerca automaticamente i market codes COT se non mappati esplicitamente, quindi funziona anche se la struttura dati cambia leggermente.