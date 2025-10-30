# Update COT Reports

⚠️ **ATTENZIONE: POWERSHELL NON SUPPORTA `&&`** ⚠️
- **NON usare mai** `&&` per concatenare comandi
- **SEMPRE** eseguire comandi separatamente, uno alla volta
- Questo è fondamentale per evitare errori di sintassi

Esegui automaticamente lo script `scripts/cot/update_cot_pipeline.py` per scaricare, convertire e sincronizzare i dati COT più recenti disponibili. Mostra SOLO l'output raw dello script, senza aggiungere analisi o interpretazioni.

**Cosa fa lo script:**
1. Verifica ultima data disponibile online vs ultima data scaricata
2. Scarica nuovi report COT se disponibili (solo se necessario)
3. Converte CSV->Parquet per i nuovi file scaricati
4. Sincronizza tutti i file Parquet nel database DuckDB (crea/aggiorna tabella cot_disagg)
5. Fornisce summary delle operazioni

**Cosa fare (in ordine):**
1. **IMPORTANTE - Installa dipendenze (se non già fatto):**
   ```bash
   pip install -r requirements.txt
   ```
   Se non hai ancora installato le dipendenze, questo è il primo passo obbligatorio.

2. Identifica il percorso workspace root: `C:\Users\a566269\Desktop\Cot_Report_MIC`
3. **IMPORTANTE - Gestione directory:**
   - Se già nella directory corretta, esegui direttamente il comando Python
   - Se serve cambiare directory, fallo in un comando separato PRIMA
   
4. Esegui i comandi Python in sequenza (SEMPRE separati, MAI con `&&`):
   
   **❌ ERRORE CRITICO DA EVITARE (NON FUNZIONA IN POWERSHELL):**
   ```bash
   # ❌ MAI FARE QUESTO - PowerShell darà errore di sintassi
   cd "C:\Users\a566269\Desktop\Cot_Report_MIC" && python scripts/cot/update_cot_pipeline.py && python scripts/cot/sync_complete.py
   ```
   
   **✅ FORMA CORRETTA - SEMPRE comandi separati:**
   
   **Opzione A: Se già nella directory corretta:**
   - Esegui PRIMA lo script 1, POI lo script 2 in chiamate separate
   ```bash
   python scripts/cot/update_cot_pipeline.py
   # (aspetta completamento)
   python scripts/cot/sync_complete.py
   ```
   
   **Opzione B: Se serve cambiare directory:**
   - Fai PRIMA il cd in una chiamata separata
   - POI esegui script 1 in una chiamata separata
   - POI esegui script 2 in una chiamata separata
   ```bash
   cd "C:\Users\a566269\Desktop\Cot_Report_MIC"
   # (aspetta completamento)
   python scripts/cot/update_cot_pipeline.py
   # (aspetta completamento)
   python scripts/cot/sync_complete.py
   ```
   
   **REGOLA FERREA: Un comando per volta, MAI concatenare con `&&`**

5. Mostra TUTTO l'output generato da entrambi gli script esattamente come appare, senza modifiche o analisi aggiuntive
6. Se ci sono errori, mostra il messaggio di errore completo

**IMPORTANTE:**
- NON aggiungere osservazioni, interpretazioni o analisi personali
- NON commentare i risultati
- Mostra SOLO l'output dello script così com'è
- Se lo script genera output, copialo direttamente senza modifiche

**Output attesi:**

**Se già aggiornato:**
```
[OK] Gia scaricati i piu recenti COT report
[OK] Verifica parquet eseguita senza integrazioni
Loading 2025...
  -> X righe caricate
TOTAL: X rows
Date range: YYYY-MM-DD - YYYY-MM-DD
[OK] DuckDB sync: X rows
Date range in DB: YYYY-MM-DD - YYYY-MM-DD
[OK] Complete!
```

**Se ci sono nuovi dati:**
```
[DOWNLOAD] Scaricando dati 2025...
[OK] Scaricati X righe
[CONVERT] cot_legacy_2025.txt -> legacy_futures_2025.parquet
[OK] Convertiti X file(s) in Parquet
Loading 2025...
  -> X righe caricate
TOTAL: X rows
Date range: YYYY-MM-DD - YYYY-MM-DD
[OK] DuckDB sync: X rows
Date range in DB: YYYY-MM-DD - YYYY-MM-DD
[OK] Complete!
```

**Dipendenze:**
- Tutte le dipendenze devono essere installate: `pip install -r requirements.txt`
- Se non installate, lo script indicherà l'errore
- File `requirements.txt` contiene: `cot-reports`, `pandas`, `duckdb`, `pyarrow`

