# Update COT Reports

Esegui automaticamente lo script `scripts/cot/update_cot_pipeline.py` per scaricare, convertire e sincronizzare i dati COT più recenti disponibili. Mostra SOLO l'output raw dello script, senza aggiungere analisi o interpretazioni.

**Cosa fa lo script:**
1. Verifica ultima data disponibile online vs ultima data scaricata
2. Scarica nuovi report COT se disponibili (solo se necessario)
3. Converte CSV->Parquet per i nuovi file scaricati
4. Fornisce summary delle operazioni

**Cosa fare (in ordine):**
1. Identifica il percorso workspace root: `C:\Users\a566269\Desktop\Cot_Report_MIC`
2. **IMPORTANTE - Gestione directory:**
   - Se già nella directory corretta, esegui direttamente il comando Python
   - Se serve cambiare directory, fallo in un comando separato PRIMA
   
3. Esegui il comando Python in modo diretto:
   ```bash
   python scripts/cot/update_cot_pipeline.py
   ```
   
   **❌ ERRORI COMUNI DA EVITARE (NON FUNZIONANO IN POWERSHELL):**
   - ❌ `cd "C:\Users\a566269\Desktop\Cot_Report_MIC" && python scripts/cot/update_cot_pipeline.py`
   - ❌ Qualsiasi comando concatenato con `&&` (PowerShell NON supporta `&&`)
   - ❌ Comandi su più righe con `&&`
   
   **✅ FORMA CORRETTA:**
   - ✅ Se nella directory: `python scripts/cot/update_cot_pipeline.py`
   - ✅ Se serve cambiare directory:
     ```bash
     cd "C:\Users\a566269\Desktop\Cot_Report_MIC"
     python scripts/cot/update_cot_pipeline.py
     ```
   - ✅ Usa SEMPRE comandi separati, NON concatenati con `&&`

4. Mostra TUTTO l'output generato esattamente come appare, senza modifiche o analisi aggiuntive
5. Se ci sono errori, mostra il messaggio di errore completo

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
```

**Se ci sono nuovi dati:**
```
[DOWNLOAD] Scaricando dati 2025...
[OK] Scaricati X righe
[CONVERT] cot_legacy_2025.txt -> legacy_futures_2025.parquet
[OK] Convertiti X file(s) in Parquet
```

**Dipendenze:**
- Libreria `cot_reports` installata: `pip install cot-reports`
- Se non installata, lo script indicherà l'errore

