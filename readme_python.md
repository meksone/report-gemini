# Script Python — Preparazione Dati per il Dashboard

Questi script trasformano il log grezzo esportato da Google Workspace Admin in
i tre file CSV pronti per essere caricati nel dashboard.

## Prerequisiti

- Python 3.x (nessuna dipendenza esterna, solo libreria standard `csv`)
- Il log grezzo deve chiamarsi `_logV2.csv` e usare `;` come separatore
- Encoding atteso del file sorgente: **latin-1** (tipico export Google Admin)

---

## Flusso di elaborazione

```
_logV2.csv  (raw, latin-1, ;)
      │
      ▼  [1] add_event_id.py
_logV2_with_eventID.csv  (utf-8, aggiunto eventID)
      │
      ├──▶  [2a] build_features.py  ──▶  _logV2_normalized.csv  +  features.csv
      │
      └──▶  [2b] split_log.py       ──▶  _logV2_events.csv      +  _logV2_features.csv
```

Gli script `build_features.py` e `split_log.py` partono entrambi da
`_logV2_with_eventID.csv` ma producono output diversi (vedi dettagli sotto).
Eseguire **sempre prima** `add_event_id.py`.

---

## Script 1 — `add_event_id.py`

**Scopo:** aggiunge una colonna `eventID` univoca a ogni riga del log grezzo e
converte l'encoding da latin-1 a UTF-8.

**Input:**
| File | Separatore | Encoding |
|---|---|---|
| `_logV2.csv` | `;` | latin-1 |

**Output:**
| File | Contenuto |
|---|---|
| `_logV2_with_eventID.csv` | Log originale + colonna `eventID` (es. `sol-ev1`, `sol-ev2`, …) |

**Esecuzione:**
```bash
python add_event_id.py
```

---

## Script 2a — `build_features.py`

**Scopo:** separa le colonne "feature" dal log e crea una tabella di lookup
deduplicata (`features.csv`). Il log normalizzato mantiene solo le colonne
evento + un riferimento `featureID`.

Ogni combinazione univoca di `Feature_source + Action + Event_category + App_name`
diventa un record distinto in `features.csv` con ID `sol-feat1`, `sol-feat2`, ecc.

**Input:**
| File | Separatore | Encoding |
|---|---|---|
| `_logV2_with_eventID.csv` | `;` | utf-8 |

**Output:**
| File | Colonne | Descrizione |
|---|---|---|
| `_logV2_normalized.csv` | `eventID, Date, Event, Description, Actor, featureID` | Log pulito con FK verso features |
| `features.csv` | `featureID, Feature_source, Action, Event_category, App_name` | Lookup feature deduplicato — **questo è il file "Features" da caricare nel dashboard** |

**Esecuzione:**
```bash
python build_features.py
```

---

## Script 2b — `split_log.py`

**Scopo:** alternativa più semplice a `build_features.py`. Divide il log in due
file separati mantenendo `eventID` come chiave di join, senza deduplicare le feature.

**Input:**
| File | Separatore | Encoding |
|---|---|---|
| `_logV2_with_eventID.csv` | `;` | utf-8 |

**Output:**
| File | Colonne | Descrizione |
|---|---|---|
| `_logV2_events.csv` | `eventID, Date, Event, Description, Actor` | Solo colonne evento/attore |
| `_logV2_features.csv` | `eventID, Feature_source, Action, Event_category, App_name` | Solo colonne feature (una riga per evento, non deduplicato) |

**Esecuzione:**
```bash
python split_log.py
```

---

## Quale flusso usare?

| Scenario | Flusso consigliato |
|---|---|
| Dashboard standard (ZIP o caricamento separato) | `add_event_id` → `build_features` → carica `features.csv` + `_logV2_normalized.csv` |
| Analisi/debug manuale con join semplice | `add_event_id` → `split_log` |

---

## File da caricare nel dashboard

Dopo aver eseguito `add_event_id.py` + `build_features.py`:

| Pulsante dashboard | File da caricare |
|---|---|
| **1. Load Registry** | `Anagrafica_Report_*.csv` (export da Google Admin) |
| **2. Load Features** | `features.csv` |
| **3. Load Logs** | `_logV2_normalized.csv` |

Oppure comprimi i tre file in un unico ZIP e usa **Load ZIP (all-in-one)**.
Il nome dei file nel ZIP deve contenere le parole chiave: `registry` o `anagrafica`,
`features`, `logs` o `log`.
