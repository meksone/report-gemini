# Guida alla Lettura — Gemini AI Executive Report

## Architettura del Dashboard

### Pipeline dei Dati

Il dashboard si alimenta di tre CSV (o un unico ZIP) caricati dall'utente:

1. **Registry CSV** — anagrafica dipendenti. Campi: `log` (email), `isactive`, `isexternal`, `country`, `company`, `businessareas`, `workspace_orgunit` (codice reparto).
2. **Features CSV** — tabella di lookup che mappa `featureID` → `Action`, `Feature_source`, `Event_category`, `App_name`.
3. **Logs CSV** — log grezzo delle attività. Campi: `featureID`, `date`, `actor` (email), `Event`, `Description`.

Elaborazione: i log vengono letti in streaming a blocchi tramite PapaParse. Ogni riga viene arricchita unendo i dati dell'anagrafica (per email) e del Features (per featureID), aggiungendo il contesto organizzativo.

---

## Classificazione Utenti (4 categorie)

Ogni attore presente nei log viene classificato al momento dell'elaborazione:

| Tipo | Logica |
|---|---|
| **Internal Users** | Presente in anagrafica, `isExternal=0`, codice reparto NON contiene `shared/condivis/servizi/generic` |
| **Shared Mailboxes** | Presente in anagrafica, `isExternal=0`, codice reparto CONTIENE le keyword condivise |
| **External/Consultants** | Presente in anagrafica, `isExternal=1` |
| **Unmapped** | Email NON trovata in anagrafica |

---

## Classificazione Maturità (concetto centrale)

Ogni azione è classificata in uno dei due livelli di maturità, **definiti staticamente nel dizionario `ACTIONS_DICT`**:

- **Intentional (Intenzionale)** — l'utente ha attivato attivamente una funzione AI o scritto un prompt (`custom_prompt`, `conversation`, `summarize`, `generate_document`, ecc.)
- **Proactive (Proattivo)** — suggerimento o azione generata automaticamente dal sistema senza input diretto dell'utente (`auto_proofread`, `suggest_replies`, `catch_me_up`, `classic_use_case_meet_studio_lighting`, ecc.)

**KPI Maturità** = `Azioni intenzionali / Totale azioni × 100`. Un valore alto indica utenti che usano attivamente l'AI tramite prompt, non solo come destinatari passivi di suggerimenti di sistema.

---

## Calcolo dei KPI

| KPI | Formula |
|---|---|
| **Adoption Rate** | `Utenti attivi unici (escluso Unmapped) ÷ Dipendenti attivi in anagrafica × 100` |
| **Interaction Volume** | Conteggio grezzo di tutte le righe di log che soddisfano il filtro attivo |
| **Top Impacted App** | App con il maggior numero di azioni (da lookup `featureID → appName`) |
| **Maturity %** | Azioni intenzionali ÷ totale azioni |

L'Adoption Rate esclude deliberatamente gli utenti **Unmapped** da numeratore e denominatore: conta solo gli utenti verificabili nell'anagrafica aziendale.

---

## Struttura degli Aggregatori

Durante il parsing dei log, tutti i dati vengono pre-aggregati nell'oggetto `agg`, una struttura annidata indicizzata per `[maturità: intentional|proactive][tipo utente: users|shared|external|unmapped]`. Questo rende il filtraggio dei grafici istantaneo, senza rileggere il CSV.

Aggregatori tracciati:

| Aggregatore | Contenuto |
|---|---|
| `agg.total` | Totali generali |
| `agg.app` | Per nome applicazione |
| `agg.cat` | Per categoria AI (Content Generation, Meeting Enhancement, ecc.) |
| `agg.country` / `agg.company` / `agg.area` | Per dimensione organizzativa |
| `agg.trend` | Serie temporale giornaliera (data → conteggi) |
| `agg.maturity` | Split intenzionale vs proattivo |
| `agg.eventCategory` | Categorie evento Google raw |
| `agg.featureSource` | Gruppi di feature source |
| `agg.gmailActions` | Drill-down specifico Gmail |
| `agg.userStats` | Totali per utente + conteggio intenzionale (per la Top 20) |
| `agg.uniqueActorsIntentional/Proactive` | Set di email distinte (per deduplicazione Adoption Rate) |

---

## Catena di Mapping Feature → Categoria (3 livelli)

```
Chiave azione raw (dal log)
  → ACTIONS_DICT → { event_category, maturity, description }
    → EVENT_CATEGORY_DICT → { feature_source }
      → FEATURE_SOURCE_DICT → { category, desc }
```

**Esempio:** `auto_proofread` → `event_category: proofread` → `feature_source: help_me_write` → `category: Content Generation`

`ACTION_LABEL_MAP` è una mappa piatta parallela usata specificamente per etichettare la dimensione **App** (es. `conversation` → "Side panel", `generate_videos_in_product` → "Vids").

---

## Viste per Tab

| Tab | Tipo Grafico | Opzioni Metrica |
|---|---|---|
| **Overview** | Trend lineare + numeri hero + Top 20 leaderboard | — |
| **Country** | Barre orizzontali | Volume o % Adoption Rate |
| **Company** | Barre orizzontali | Volume o % Adoption Rate |
| **Business Areas** | Barre orizzontali | Volume |
| **Apps & Maturity** | Donut (app) + Torta (maturità) + barre drill-down Gmail | — |
| **Interaction Types** | Torta (event categories) + Donut (feature sources) | — |
| **Use Cases** | Barre orizzontali (categorie AI) + tabella legenda statica | — |

---

## Sistema di Qualità dei Dati

Durante il parsing dei log, ogni email univoca viene verificata una sola volta nell'anagrafica (il Set `checkedUsers` evita controlli doppi). Le email non presenti → aggiunte alla Map `anomalousUsers` con la data dell'ultima attività rilevata. Se esistono anomalie, compare un banner rosso con contatore e pulsante per esportare il report CSV degli utenti anomali.

---

## Filtri Globali (applicati in modo reattivo, senza re-parsing)

- **Filtro tipo utente**: Tutti / Interni / Shared / Esterni / Unmapped
- **Filtro maturità**: Tutte le interazioni / Solo Intenzionali / Solo Proattive

Entrambi i filtri rielaborano i dati pre-aggregati tramite `filterNode()` — nessuna rilettura del CSV richiesta.

---

## Top 20 Change Agents

La classifica mostra i 20 utenti con il maggior numero di **azioni intenzionali** (prompt attivi), ordinati per `userStats[email].advanced`. La barra di progresso per ogni utente mostra la percentuale di utilizzo intenzionale sul totale delle sue azioni. Gli utenti Unmapped sono segnalati con un'icona di avviso.
