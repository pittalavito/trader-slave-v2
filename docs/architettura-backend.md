# Architettura del backend

Stato: **decisa insieme a Vito** il 26 novembre 2026. Le righe segnate *proposta* non sono ancora state discusse.

Questo documento fissa struttura e librerie del backend. Ogni fase della [roadmap](https://pittalavito.github.io/trader-slave-v2/) aggiunge pezzi dentro questa struttura, senza cambiarla.

## Principi

1. **Un solo codice, due processi.** L'API risponde al frontend; il motore (worker) fa girare le strategie. Usano gli stessi moduli e lo stesso database.
2. **La strategia è solo il segnale.** Rischio, dimensionamento, esecuzione e portafoglio sono comuni a tutte (i sei livelli già presenti in `app/engine`).
3. **Lo stesso motore per backtest, simulazione e soldi veri.** Cambia solo il livello di esecuzione (simulato o reale) e la sorgente dei dati (storico o in tempo reale). Così il backtest prova esattamente il codice che andrà in produzione.
4. **Exchange e wallet dietro interfacce.** Kraken e Solana stanno nella cartella `clients/` con un'interfaccia comune; nei test e nel backtest si usa il client simulato.
5. **Soldi sempre in `Decimal`**, mai in numeri a virgola mobile.
6. **Tutto in UTC** nel backend; il fuso orario si applica solo nel frontend.

## Librerie

| Area | Scelta | Perché | Alternativa scartata |
| --- | --- | --- | --- |
| Linguaggio | Python 3.12 | Già deciso; ecosistema migliore per dati e trading | |
| Database | **PostgreSQL 16 con TimescaleDB** ✅ | Postgres normale più tabelle ottimizzate per serie temporali: le candele a 1 minuto diventano milioni di righe, e 5m, 15m, 1h, 1g si calcolano da sole (aggregati continui) | Postgres semplice; file Parquet |
| Accesso al database | **SQLAlchemy 2** (asincrono) + **psycopg 3** | Standard di fatto, già nello scheletro | SQLModel, Tortoise |
| Migrazioni | **Alembic** | Ogni modifica alle tabelle è un file versionato | |
| API | **FastAPI** + **Pydantic v2** + pydantic-settings | Già nello scheletro; asincrona, documentazione automatica dell'API | Django |
| Comandi API → motore | **Tabella di comandi + LISTEN/NOTIFY di Postgres** ✅ | Il comando arriva in meno di un secondo e resta salvato anche se il motore si riavvia; nessun servizio in più | Redis; API HTTP nel motore |
| Kraken | **ccxt** (`krakenfutures`) ✅ | Dati, ordini e WebSocket già pronti; firme, limiti e riconnessioni gestiti dalla libreria | Client scritto da noi; python-kraken-sdk |
| Solana | **Da decidere** ⏸ | Si sceglie all'inizio della fase "Soldi veri: strategia A". Per ora `clients/solana` è solo l'interfaccia | Jupiter + solders; DEX diretto; servizio esterno |
| Login e ruoli | **JWT nostro** (pyjwt) + password **argon2** (pwdlib) ✅ | Poco codice, nessun servizio esterno; i ruoli stanno nel database | fastapi-users; Auth0/Keycloak |
| Segreti degli utenti | **Cifrati nel database** con cryptography (Fernet) ✅ | La chiave per decifrarli sta solo nel `.env` del server. Miglioramenti nella fase "Rafforzare la sicurezza" della roadmap | Cassaforte esterna (per ora); solo `.env` |
| Dipendenze | **uv** con `uv.lock` ✅ | Versioni identiche in locale, CI e server | Poetry; pip |
| Qualità e test | **ruff** + **mypy** + **pytest** su Postgres vero in Docker ✅ | Stile, tipi e test a ogni PR | |
| Chiamate HTTP | **httpx** *(proposta)* | Asincrono, usato anche nei test | requests |
| Calcoli e indicatori | **pandas** + **numpy** *(proposta)* | Standard per backtest e indicatori; la libreria di indicatori si sceglie con le strategie | polars |
| Ciclo del motore | **asyncio** allineato alla chiusura delle candele *(proposta)* | Ogni strategia decide alla chiusura della candela del suo blocco | APScheduler, Celery |
| Osservabilità | **structlog** in JSON + **OpenTelemetry** ✅ | Vedi "Regole di programmazione": un decoratore comune dà log e tracce uniformi | Solo log; log scritti a mano |
| Notifiche | **httpx** verso l'API di Telegram *(proposta)* | Bastano poche chiamate | python-telegram-bot |

✅ deciso · ⏸ rimandato

## Struttura delle cartelle

```
backend/
├── pyproject.toml, uv.lock
├── alembic/                  migrazioni del database
├── app/
│   ├── main.py               avvio dell'API
│   ├── worker.py             avvio del motore
│   ├── core/                 la parte comune a tutto il resto (vedi sotto)
│   │   ├── config.py         configurazione da .env (Pydantic)
│   │   ├── observability.py  decoratore @observed, log e tracce
│   │   ├── errors.py         gerarchia delle eccezioni
│   │   ├── types.py          Money, Symbol, Timeframe, id per entità
│   │   ├── clock.py          orologio vero e orologio del backtest
│   │   ├── security.py       JWT, password, cifratura dei segreti
│   │   └── container.py      assemblaggio dei componenti per API e motore
│   ├── db/                   connessione e classe base dei modelli
│   ├── api/                  endpoint HTTP, uno per area, solo traduzione richiesta/risposta
│   ├── modules/              la logica, divisa per area
│   │   ├── users/            utenti, ruoli, inviti degli osservatori
│   │   ├── portfolios/       portafogli, strategie attive, limiti di rischio, operazioni
│   │   ├── market/           candele, simboli, aggiornamento dei dati
│   │   ├── strategies/       le strategie (livello segnale), una per file
│   │   ├── backtest/         esecuzione e report dei backtest
│   │   └── notifications/    Telegram
│   ├── engine/               i sei livelli e il ciclo del motore
│   └── clients/              collegamenti al mondo esterno, stessa interfaccia
│       ├── kraken/           dati e ordini sui futures perpetui (ccxt)
│       ├── solana/           wallet e scambi (libreria da decidere)
│       └── simulated/        esecuzione simulata per backtest e paper trading
└── tests/
```

Ogni modulo in `modules/` ha la stessa forma: `models.py` (tabelle), `schemas.py` (dati in entrata e uscita dall'API), `service.py` (logica), `repository.py` (query). Gli endpoint in `api/` chiamano solo i `service`.

## Regole di programmazione e core

Decise insieme a Vito il 26 novembre 2026. `app/core/` contiene solo ciò che serve a tutti i moduli e non dipende da nessun modulo.

### Modelli tipizzati ✅
- **Ai bordi Pydantic in modalità strict**: dati che entrano o escono dall'API, configurazione, risposte di Kraken e degli altri servizi. Un dato sbagliato si ferma lì.
- **Dentro dataclass immutabili** (`frozen=True, slots=True`): candele, segnali, ordini, posizioni nel motore. Veloci nel backtest su milioni di candele.
- **mypy in modalità strict** su tutto il backend: la PR non passa se un tipo non torna.

### Osservabilità ✅
- Un decoratore **`@observed`** in `core/observability.py` da mettere sui metodi importanti (servizi, livelli del motore, client). Registra inizio, durata, esito ed eventuale errore.
- **Log JSON con structlog** e **tracce OpenTelemetry**. Ogni richiesta API e ogni ciclo del motore ha un id che lega tutti i passi, così si ricostruisce perché una strategia ha aperto o chiuso.
- In locale le tracce si leggono nei log; più avanti si possono mandare a Grafana o simili senza cambiare il codice.
- `@observed(fields=[...])` scrive nel log solo gli argomenti scelti a mano (per esempio simbolo e timeframe), così chiavi e password non finiscono mai nei log per sbaglio.
- Per ora gli span si vedono nel terminale con `OTEL_CONSOLE=true`; un viewer grafico (Grafana, Jaeger) arriva più avanti.

### Errori ✅
Una gerarchia di eccezioni in `core/errors.py`, ognuna con un codice stabile e un messaggio:

| Eccezione | Quando | Risposta API |
| --- | --- | --- |
| `AppError` | base di tutte | 500 |
| `ValidationError` | dato in ingresso non valido | 422 |
| `AuthenticationError` | token mancante, scaduto o sbagliato | 401 |
| `NotFoundError` | risorsa inesistente | 404 |
| `PermissionDeniedError` | ruolo o proprietario sbagliato | 403 |
| `DomainError` | regola violata (es. limite di rischio, leva oltre il tetto) | 409 |
| `ExternalServiceError` | Kraken, Solana, Telegram non rispondono o rifiutano | 502 |

Un solo gestore nell'API le traduce in risposte; il decoratore `@observed` le registra con il loro codice. Nel motore un errore di una strategia non ferma le altre.

### Tipi comuni e orologio ✅
- `Money`: importo `Decimal` più valuta; sommare valute diverse è un errore.
- `Symbol` e `Timeframe`: tipi dedicati, non stringhe libere.
- Id distinti per entità (`UserId`, `PortfolioId`, `StrategyId`…): mypy impedisce di passare l'id sbagliato.
- `Clock`: interfaccia con `now()`. In produzione l'orologio vero (UTC), nel backtest l'orologio del motore che avanza candela per candela. Nessun modulo chiama `datetime.now()` direttamente.

### Dipendenze tra componenti ✅
- Ogni classe riceve ciò che le serve **nel costruttore**, tipizzato con un `Protocol` (es. `ExchangeClient`, `Clock`, `CandleRepository`).
- Un unico punto, `core/container.py`, assembla i componenti veri per API e motore; il backtest e i test assemblano quelli simulati.
- `Depends` di FastAPI si usa solo negli endpoint, per prendere i servizi dal container e l'utente autenticato.

## Come gira

- **API** (`uvicorn app.main:app`): autenticazione, gestione di portafogli e strategie, lancio dei backtest, lettura di risultati e registro.
- **Motore** (`python -m app.worker`): un unico processo asincrono che
  1. aggiorna le candele appena si chiudono;
  2. per ogni strategia attiva, alla chiusura della candela del suo blocco, esegue un ciclo dei sei livelli;
  3. ascolta i comandi dall'API (avvia, ferma, emergenza);
  4. controlla le connessioni e segnala dati fermi.
- **Backtest**: girano nel motore come lavori in coda, così l'API resta veloce anche con backtest lunghi.

## Da decidere più avanti

- Libreria di indicatori tecnici: con le regole delle strategie.
- Fonte dei dati Solana definitiva: all'inizio della fase "Dati di mercato".
- Libreria per gli scambi su Solana: all'inizio della fase "Soldi veri: strategia A".
- Se i backtest diventano pesanti, un processo separato solo per loro.
