# Scenari di Errore e Edge Cases - Comandi COT Reports

Documentazione completa degli scenari di errore possibili per i comandi `/update` e `/analisi_ultima_settimana` e come gestirli.

---

## 🔴 COMANDO `/update` - Scenari di Errore

### 1. Libreria `cot_reports` Non Installata

**Errore:**
```
[ERROR] Libreria cot_reports non installata
Installa con: pip install cot-reports
```

**Causa:** Dipendenze non installate o ambiente virtuale non attivato.

**Soluzione:**
```bash
pip install -r requirements.txt

# Verifica installazione
python -c "import cot_reports; print('OK')"
```

**Check automatico:** Lo script verifica automaticamente e mostra questo messaggio.

---

### 2. Download Fallito - Problemi di Rete

**Errore:**
```
[ERROR] Download fallito: Connection timeout
# oppure
[ERROR] Download fallito: [Errno 11001] getaddrinfo failed
```

**Cause possibili:**
- Connessione internet assente
- Firewall/proxy blocca connessione
- Server CFTC temporaneamente non disponibile
- Timeout durante download file grande

**Soluzioni:**
1. **Verifica connessione:**
   ```bash
   ping www.cftc.gov
   ```

2. **Riprova dopo alcuni minuti** (server CFTC potrebbe essere temporaneamente sovraccarico)

3. **Controlla firewall/antivirus** - potrebbero bloccare connessioni Python

4. **Download manuale** (ultima risorsa):
   - Vai su https://www.cftc.gov/dea/newcot/CotHistAllFutures.txt
   - Salva file in `data/cot/csv/cot_legacy_YYYY.txt`
   - Rielabora con: `python scripts/cot/auto_convert_csv_to_parquet.py`

---

### 3. File CSV Corrotto o Incompleto

**Errore:**
```
[ERROR] Conversione cot_legacy_2025.txt fallita: Error tokenizing data
# oppure
[ERROR] Conversione cot_legacy_YYYY.txt fallita: 'As of Date in Form YYYY-MM-DD' not found
```

**Cause possibili:**
- Download interrotto a metà
- File parzialmente corrotto
- Formato file cambiato dalla CFTC

**Soluzione:**
1. **Elimina file corrotto:**
   ```bash
   # Windows PowerShell
   Remove-Item "data\cot\csv\cot_legacy_YYYY.txt"
   ```

2. **Ridownload:**
   ```bash
   python scripts/cot/update_cot_pipeline.py
   ```

3. **Verifica integrità:**
   - File deve essere > 1 MB (dimensioni tipiche: 5-50 MB per anno)
   - Deve iniziare con header COT (prima riga contiene "As of Date")

---

### 4. Spazio Disco Insufficiente

**Errore:**
```
[ERROR] Download fallito: No space left on device
# oppure
OSError: [Errno 28] No space left on device
```

**Causa:** Disco pieno - i file COT possono essere grandi (50-100 MB per anno completo).

**Soluzione:**
1. **Libera spazio:**
   ```bash
   # Windows: Verifica spazio libero
   Get-PSDrive C | Select-Object Used,Free
   ```

2. **Elimina file vecchi** (se necessario):
   ```bash
   # Elimina report vecchi (>30 giorni)
   Get-ChildItem "data\reports\*.txt" | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item
   ```

3. **Limita anni scaricati:**
   - Modifica script per scaricare solo anno corrente
   - Elimina CSV dopo conversione in Parquet (Parquet è più piccolo)

**Dimensione media file:**
- CSV: ~20-50 MB per anno
- Parquet: ~5-10 MB per anno
- Database DuckDB: ~10-20 MB totale

---

### 5. Permessi di Scrittura Insufficienti

**Errore:**
```
PermissionError: [Errno 13] Permission denied: 'data\\cot\\csv\\cot_legacy_2025.txt'
```

**Causa:** Directory `data/` non scrivibile o file già aperto in altro programma.

**Soluzione:**
1. **Verifica permessi directory:**
   ```bash
   # Windows: Controlla permessi
   icacls "data\cot\csv"
   ```

2. **Chiudi programmi che usano i file:**
   - Excel/apre `cot_legacy_*.txt`
   - Editor di testo che hanno file aperti
   - Altri script Python che stanno usando il database

3. **Esegui come amministratore** (se necessario):
   ```bash
   # PowerShell come amministratore
   python scripts/cot/update_cot_pipeline.py
   ```

---

### 6. Database DuckDB Bloccato

**Errore:**
```
RuntimeError: IO Error: Unable to acquire lock
# oppure
duckdb.DatabaseException: Database is locked
```

**Causa:** Un altro processo sta usando il database (es: altra istanza dello script, query aperta).

**Soluzione:**
1. **Chiudi altri script Python** che potrebbero avere il DB aperto

2. **Verifica processi attivi:**
   ```bash
   # Windows PowerShell
   Get-Process python | Select-Object Id,ProcessName,StartTime
   ```

3. **Se necessario, elimina lock file:**
   ```bash
   # ATTENZIONE: Solo se sei sicuro che nessun processo sta usando il DB
   # Il lock viene rilasciato automaticamente quando il processo termina
   ```

4. **Riprova dopo qualche secondo** (lock viene rilasciato automaticamente)

---

### 7. Nessun Dato Disponibile Online (Fine Settimana/Ferie)

**Output:**
```
Ultima data online: None
Ultima data scaricata: 2025-09-23
[OK] Gia scaricati i piu recenti COT report
```

**Causa:** CFTC non pubblica report nel weekend o giorni festivi. Il report viene pubblicato tipicamente il venerdì sera (US time).

**Comportamento normale:** Non è un errore. Lo script rileva correttamente che hai già i dati più recenti disponibili.

**Verifica manuale:**
- Vai su https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
- Verifica ultima data pubblicata

---

## 🟡 COMANDO `/analisi_ultima_settimana` - Scenari di Errore

### 1. Database Vuoto o Non Inizializzato

**Errore:**
```
No data available
```

**Causa:** Database DuckDB non contiene dati o tabella `cot_disagg` non esiste.

**Soluzione:**
```bash
# 1. Scarica i dati
python scripts/cot/update_cot_pipeline.py

# 2. Sincronizza database
python scripts/cot/sync_complete.py

# 3. Verifica database
python scripts/cot/query.py "SELECT COUNT(*) FROM cot_disagg"
```

**Check preventivo:**
- Verifica esistenza file: `data/duckdb/cot.db` (deve esistere ed essere > 0 byte)
- Verifica tabelle: `python scripts/cot/query.py "SHOW TABLES"`

---

### 2. Ultima Data Non Trovata

**Output:**
```
(Nessun output o errore silenzioso)
```

**Causa:** Database esiste ma non contiene date valide o colonna `report_date` mancante.

**Debug:**
```bash
# Verifica contenuto database
python scripts/cot/query.py "SELECT MAX(report_date) FROM cot_disagg"
python scripts/cot/query.py "SELECT COUNT(*) FROM cot_disagg"
```

**Soluzione:**
1. **Ricostruisci database:**
   ```bash
   # Elimina e ricostruisci
   Remove-Item "data\duckdb\cot.db"
   python scripts/cot/sync_complete.py
   ```

2. **Verifica file Parquet:**
   ```bash
   # Controlla che esistano file Parquet
   Get-ChildItem "data\cot\parquet\*.parquet"
   ```

---

### 3. Market Codes Non Trovati per Alcuni Strumenti

**Output:**
```
2025-09-23 (ultimo report disponibile)

AUD: DELTA settimana -8,430 ...
EUR: DELTA settimana -3,414 ...
S&P 500: (manca nell'output)
GOLD: (manca nell'output)
```

**Causa:** Lo script non trova alcuni market codes nel database. Normalmente li cerca automaticamente, ma potrebbero:
- Non essere presenti nel database
- Avere nomi diversi da quelli attesi
- Essere stati rimossi dalla CFTC

**Soluzione:**
1. **Verifica manuale market codes:**
   ```bash
   python scripts/cot/query.py "SELECT DISTINCT contract_market_code, market_and_exchange FROM cot_disagg WHERE market_and_exchange LIKE '%GOLD%'"
   ```

2. **Aggiungi manualmente** in `auto_report.py` se trovi il code corretto:
   ```python
   INSTRUMENTS = {
       "GOLD": ("TROVATO_CODE", "GOLD MARKET NAME"),
       # ...
   }
   ```

3. **Ricerca automatica migliorata:** Lo script cerca automaticamente, ma potrebbe non trovare varianti dei nomi.

**Strumenti spesso problematici:**
- S&P 500 (varie varianti di nomi)
- NASDAQ (diversi codici per diversi contratti)
- VIX (codice cambiato nel tempo)

---

### 4. File Report Non Scrivibile

**Errore:**
```
(Nessun errore visibile, ma file report non viene creato)
```

**Causa:** Directory `data/reports/` non scrivibile o file aperto in altro programma.

**Soluzione:**
1. **Verifica directory:**
   ```bash
   Test-Path "data\reports"
   # Se False, crea directory
   New-Item -ItemType Directory -Path "data\reports" -Force
   ```

2. **Chiudi editor** che potrebbe avere `cot_report_utf8.txt` aperto

3. **Verifica permessi:**
   ```bash
   icacls "data\reports"
   ```

---

### 5. Connessione Database Fallita

**Errore:**
```
RuntimeError: IO Error: Unable to open database
# oppure
duckdb.DatabaseException: Database file corrupted
```

**Cause possibili:**
- File database corrotto
- Database bloccato da altro processo
- Path database errato

**Soluzione:**
1. **Verifica integrità database:**
   ```bash
   python scripts/cot/query.py "SELECT COUNT(*) FROM cot_disagg"
   ```

2. **Ricostruisci se corrotto:**
   ```bash
   # Backup (opzionale)
   Copy-Item "data\duckdb\cot.db" "data\duckdb\cot.db.backup"
   
   # Elimina e ricostruisci
   Remove-Item "data\duckdb\cot.db"
   python scripts/cot/sync_complete.py
   ```

3. **Verifica non sia bloccato:**
   - Chiudi tutti gli script Python attivi
   - Riavvia terminale se necessario

---

## 🟢 SCENARI DI WARNING (Non Bloccanti)

### 1. Dati Parziali - Solo Alcuni Anni Disponibili

**Output normale:**
```
Loading 2025...
  -> 12,430 righe caricate
```

**Se mancano anni precedenti:**
- Lo script funziona normalmente ma con meno dati storici
- **Impatto:** Analisi storiche limitate
- **Soluzione:** Scarica anni mancanti con `update_cot_pipeline.py`

---

### 2. Date Mancanti nel Range Atteso

**Output normale:**
```
Date range: 2025-01-07 - 2025-09-23
```

**Se ci sono gap nelle date:**
- Potrebbero mancare alcuni report settimanali
- **Impatto:** Minore, COT reports possono avere gap occasionali
- **Verifica:** `python scripts/cot/query.py "SELECT DISTINCT report_date FROM cot_disagg ORDER BY report_date"`

---

### 3. File Molto Vecchi da Aggiornare

**Output:**
```
Ultima data online: 2025-09-23
Ultima data scaricata: 2023-01-01
[DOWNLOAD] Scaricando dati 2025...
```

**Comportamento:** Lo script scarica automaticamente tutti gli anni mancanti (può richiedere tempo).

**Tempo stimato:**
- 1 anno: ~30-60 secondi
- 3 anni: ~2-5 minuti

---

## 📋 CHECKLIST DEBUG RAPIDO

Se qualcosa non funziona, controlla in ordine:

1. ✅ **Dipendenze installate?**
   ```bash
   pip list | Select-String "cot-reports|pandas|duckdb|pyarrow"
   ```

2. ✅ **File e directory esistono?**
   ```bash
   Test-Path "data\cot\csv"
   Test-Path "data\cot\parquet"
   Test-Path "data\duckdb\cot.db"
   ```

3. ✅ **Database contiene dati?**
   ```bash
   python scripts/cot/query.py "SELECT COUNT(*) FROM cot_disagg"
   ```

4. ✅ **Connessione internet attiva?**
   ```bash
   ping www.cftc.gov
   ```

5. ✅ **Spazio disco sufficiente?**
   ```bash
   Get-PSDrive C | Select-Object Used,Free
   ```

---

## 🔧 COMANDI DI DEBUG UTILI

```bash
# Verifica stato database
python scripts/cot/query.py "SELECT COUNT(*) as total, MIN(report_date) as min_date, MAX(report_date) as max_date FROM cot_disagg"

# Lista market codes disponibili
python scripts/cot/query.py "SELECT DISTINCT contract_market_code, market_and_exchange FROM cot_disagg LIMIT 20"

# Verifica file scaricati
Get-ChildItem "data\cot\csv\*.txt" | Select-Object Name, Length, LastWriteTime

# Verifica file Parquet
Get-ChildItem "data\cot\parquet\*.parquet" | Select-Object Name, Length

# Test connessione database
python scripts/cot/query.py "SHOW TABLES"
```

---

## 📞 SUPPORTO

Se continui ad avere problemi:

1. **Raccogli informazioni:**
   - Output completo dello script con errori
   - Versione Python: `python --version`
   - Sistema operativo
   - Versione dipendenze: `pip list`

2. **Verifica log:**
   - Controlla messaggi `[ERROR]` nell'output
   - Cerca pattern comuni in questa documentazione

3. **Riprova dopo:**
   - Riavviare terminale
   - Chiudere altri programmi che potrebbero bloccare file
   - Verificare connessione internet stabile

---

*Documentazione aggiornata: Ottobre 2025*

