# Summary - Scenari di Errore Documentati

**File principale:** `docs/COMMANDS_ERROR_SCENARIOS.md`  
**Data:** Ottobre 2025

---

## 📊 Overview Scenari Documentati

### Comando `/update` (update_cot_pipeline.py)

#### 🔴 Errori Critici (7 scenari)
1. ✅ **Libreria cot_reports non installata** - Con messaggi di errore e soluzioni
2. ✅ **Download fallito (problemi rete)** - Timeout, connessione, firewall
3. ✅ **File CSV corrotto/incompleto** - Rilevamento e recupero
4. ✅ **Spazio disco insufficiente** - Verifica e gestione spazio
5. ✅ **Permessi scrittura insufficienti** - Diagnostica e risoluzione
6. ✅ **Database DuckDB bloccato** - Lock database e recovery
7. ✅ **Nessun dato disponibile online** - Weekend/ferie CFTC (non errore)

### Comando `/analisi_ultima_settimana` (auto_report.py)

#### 🔴 Errori Critici (5 scenari)
1. ✅ **Database vuoto/non inizializzato** - Verifica e inizializzazione
2. ✅ **Ultima data non trovata** - Debug e ricostruzione database
3. ✅ **Market codes non trovati** - Ricerca manuale e aggiunta
4. ✅ **File report non scrivibile** - Permessi e directory
5. ✅ **Connessione database fallita** - Corruzione e recovery

#### 🟢 Warnings Non Bloccanti (3 scenari)
1. ✅ **Dati parziali** - Solo alcuni anni disponibili
2. ✅ **Date mancanti** - Gap nei report settimanali
3. ✅ **File molto vecchi** - Download multipli anni

---

## 🛠️ Strumenti di Debug Documentati

### Checklist Debug Rapido (5 step)
1. ✅ Verifica dipendenze installate
2. ✅ Verifica file e directory esistenti
3. ✅ Verifica database contiene dati
4. ✅ Verifica connessione internet
5. ✅ Verifica spazio disco

### Comandi Debug Utili (5 comandi)
1. ✅ Verifica stato database (count, date range)
2. ✅ Lista market codes disponibili
3. ✅ Verifica file scaricati (CSV)
4. ✅ Verifica file Parquet
5. ✅ Test connessione database

---

## 📈 Copertura Documentazione

| Categoria | Scenari | Status |
|-----------|---------|--------|
| Errori critici | 12 | ✅ 100% |
| Warnings | 3 | ✅ 100% |
| Debug tools | 10 | ✅ 100% |
| Soluzioni step-by-step | 15+ | ✅ 100% |

**Totale scenari documentati:** 15+ scenari principali + varianti

---

## 🎯 Sezioni Principali Documento

1. **Comando `/update` - Scenari Errore** (7 scenari dettagliati)
2. **Comando `/analisi_ultima_settimana` - Scenari Errore** (5 scenari critici + 3 warnings)
3. **Checklist Debug Rapido** (5 step sequenziali)
4. **Comandi Debug Utili** (5 query SQL/esempi)
5. **Supporto e Troubleshooting** (Raccolta info, log, riprova)

---

## ✅ Completezza

Tutti i principali scenari di errore sono stati:
- ✅ Identificati analizzando il codice
- ✅ Documentati con messaggi di errore esatti
- ✅ Forniti con soluzioni step-by-step
- ✅ Testati con comandi reali
- ✅ Aggiornati nel README principale

**Status:** ✅ **DOCUMENTAZIONE COMPLETA E PRONTA ALL'USO**

---

*Summary generato automaticamente - Ottobre 2025*

