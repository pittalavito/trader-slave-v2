// Contenuto della roadmap, in italiano e in inglese.
// Per aggiornare la pagina modifica solo questo file.
//
// Stato di una fase o di un'attività:
//   "done"   fatto
//   "doing"  in corso
//   "next"   prossima (solo per le fasi)
//   "paused" in pausa (solo per le fasi)
//   "todo"   da fare (si può omettere nelle attività)
// "guess" contiene le ipotesi da confermare. Il testo può contenere HTML semplice.

window.ROADMAP = {
  updated: { it: "Ultimo aggiornamento: 26 novembre 2026", en: "Last updated: 26 November 2026" },
  repo: "https://github.com/pittalavito/trader-slave-v2",

  ui: {
    title: { it: "Trader Slave · Roadmap", en: "Trader Slave · Roadmap" },
    code: { it: "Vai al codice", en: "Go to the code" },
    lead: {
      it: "Questa è la guida di quello che facciamo, una fase alla volta. Ogni fase ha un obiettivo, un elenco di attività e una condizione precisa per dire che è finita: si passa alla fase dopo solo quando quella condizione è vera. Il principio che regge tutto: <strong>nessuna strategia tocca soldi veri prima di essere stata provata sui dati storici e poi in simulazione</strong>.",
      en: "This is the guide to what we build, one phase at a time. Each phase has a goal, a list of tasks and a clear condition that says when it is finished: we move to the next phase only when that condition is true. The principle behind everything: <strong>no strategy touches real money before it has been tested on historical data and then in simulation</strong>."
    },
    status: {
      done: { it: "Fatto", en: "Done" },
      doing: { it: "In corso", en: "In progress" },
      next: { it: "Prossima", en: "Next" },
      paused: { it: "In pausa", en: "On hold" },
      todo: { it: "Da fare", en: "To do" }
    },
    guessLegend: { it: "proposta da confermare", en: "proposal to be confirmed" },
    guessLabel: { it: "Ipotesi", en: "Assumption" },
    overview: { it: "Panoramica", en: "Overview" },
    phases: { it: "Le fasi", en: "The phases" },
    hint: { it: "Clicca su una tappa per vedere attività e condizione di uscita.", en: "Click a stop to see its tasks and exit condition." },
    tasks: { it: "Attività", en: "Tasks" },
    exit: { it: "Finita quando", en: "Done when" },
    deferred: { it: "Decisioni rimandate", en: "Deferred decisions" },
    outside: { it: "Fuori da questa roadmap, per ora", en: "Out of scope, for now" },
    footer: {
      it: "Basata sulla <a href=\"https://claude.ai/artifact/QbHTxeAStTcgdfRhqdpwrE\">specifica funzionale</a>. Per modificare questa pagina: <code>site/roadmap.js</code>.",
      en: "Based on the <a href=\"https://claude.ai/artifact/QbHTxeAStTcgdfRhqdpwrE\">functional spec</a> (in Italian). To edit this page: <code>site/roadmap.js</code>."
    }
  },

  phases: [
    {
      status: "done",
      title: { it: "Fondamenta", en: "Foundations" },
      goal: {
        it: "Avere le decisioni scritte, lo scheletro dell'app e i controlli automatici.",
        en: "Have the decisions written down, the app skeleton and automatic checks."
      },
      tasks: [
        { s: "done", it: "Specifica funzionale: requisiti, ruoli, strategie A e B, blocchi di timeframe, regole di rischio", en: "Functional spec: requirements, roles, strategies A and B, timeframe blocks, risk rules" },
        { s: "done", it: "Scheletro dell'app: backend Python con il motore a sei livelli, frontend React, Docker Compose, Caddy", en: "App skeleton: Python backend with the six-layer engine, React frontend, Docker Compose, Caddy" },
        { s: "done", it: "Controlli automatici (test e build) a ogni modifica", en: "Automatic checks (tests and build) on every change" },
        { s: "done", it: "Questa roadmap pubblicata su GitHub Pages", en: "This roadmap published on GitHub Pages" }
      ],
      exit: {
        it: "Il codice si avvia in locale con Docker e i controlli automatici sono verdi.",
        en: "The code starts locally with Docker and the automatic checks are green."
      }
    },
    {
      status: "doing",
      title: { it: "Architettura backend", en: "Backend architecture" },
      goal: {
        it: "Decidere una volta per tutte struttura e librerie del backend, e prepararne lo scheletro, così ogni fase successiva aggiunge pezzi senza rifare le fondamenta.",
        en: "Decide the backend structure and libraries once and for all, and build its skeleton, so every later phase adds pieces without redoing the foundations."
      },
      tasks: [
        { s: "done", it: "Proposta di architettura: struttura delle cartelle, librerie, database, comunicazione tra API e motore", en: "Architecture proposal: folder layout, libraries, database, communication between API and engine" },
        { s: "done", it: "Scelte decise insieme a Vito (<a href=\"https://github.com/pittalavito/trader-slave-v2/blob/main/docs/architettura-backend.md\">documento</a>)", en: "Choices made together with Vito (<a href=\"https://github.com/pittalavito/trader-slave-v2/blob/main/docs/architettura-backend.md\">document</a>, in Italian)" },
        { it: "Gestione dipendenze, controlli di stile e di tipo, test con un database vero", en: "Dependency management, lint and type checks, tests against a real database" },
        { it: "Database con migrazioni versionate e prime tabelle", en: "Database with versioned migrations and the first tables" },
        { it: "Struttura a moduli per area (mercato, strategie, backtest, portafogli, utenti) con il motore a sei livelli", en: "Module layout by area (market, strategies, backtest, portfolios, users) with the six-layer engine" },
        { it: "Collegamenti verso Kraken e Solana dietro interfacce comuni, sostituibili da versioni simulate", en: "Kraken and Solana connections behind common interfaces, replaceable by simulated versions" },
        { it: "Configurazione, log strutturati e gestione sicura dei segreti", en: "Configuration, structured logs and safe secret handling" }
      ],
      exit: {
        it: "Il documento di architettura è approvato e lo scheletro del backend parte in locale con Docker, con test e controlli verdi.",
        en: "The architecture document is approved and the backend skeleton starts locally with Docker, with green tests and checks."
      }
    },
    {
      title: { it: "Architettura frontend", en: "Frontend architecture" },
      goal: {
        it: "Decidere struttura e librerie del frontend React e prepararne lo scheletro.",
        en: "Decide the React frontend structure and libraries and build its skeleton."
      },
      tasks: [
        { it: "Proposta di architettura: routing, chiamate all'API, gestione dello stato, componenti grafici, grafici delle candele", en: "Architecture proposal: routing, API calls, state management, UI components, candle charts" },
        { it: "Approvazione delle scelte da parte di Vito", en: "Choices approved by Vito" },
        { it: "Tipi generati automaticamente dall'API del backend", en: "Types generated automatically from the backend API" },
        { it: "Struttura delle pagine, tema chiaro e scuro, italiano e inglese", en: "Page layout, light and dark theme, Italian and English" },
        { it: "Controlli di stile e test", en: "Lint checks and tests" }
      ],
      exit: {
        it: "Il documento di architettura è approvato e lo scheletro del frontend mostra le pagine principali vuote collegate all'API.",
        en: "The architecture document is approved and the frontend skeleton shows the main empty pages connected to the API."
      }
    },
    {
      title: { it: "Dati di mercato", en: "Market data" },
      goal: {
        it: "Avere nel database le candele storiche e aggiornate dei mercati che useremo, per tutti e tre i blocchi di timeframe.",
        en: "Have historical and up-to-date candles for the markets we will use in the database, for all three timeframe blocks."
      },
      tasks: [
        { it: "Scaricare lo storico delle candele dei futures perpetui Kraken (per la strategia B)", en: "Download candle history for Kraken perpetual futures (for strategy B)" },
        { it: "Scaricare lo storico dei prezzi dei token sui DEX Solana (per la strategia A)", en: "Download token price history from Solana DEXs (for strategy A)" },
        { it: "Salvare le candele in PostgreSQL, a partire da 1 minuto e ricavando 5m, 15m, 30m, 1h, 4h e 1g", en: "Store candles in PostgreSQL, starting from 1 minute and deriving 5m, 15m, 30m, 1h, 4h and 1d" },
        { it: "Aggiornamento continuo: il worker aggiunge le nuove candele appena si chiudono", en: "Continuous updates: the worker adds new candles as soon as they close" },
        { it: "Controllo qualità: buchi nello storico, candele duplicate o sospette", en: "Quality checks: gaps in history, duplicate or suspicious candles" },
        { it: "Implementare il livello \"dati di mercato\" del motore leggendo dal database", en: "Implement the engine's \"market data\" layer reading from the database" }
      ],
      exit: {
        it: "Ci sono almeno 12 mesi di candele a 1 minuto per i mercati di partenza, senza buchi, e il worker le aggiorna da solo.",
        en: "There are at least 12 months of 1-minute candles for the starting markets, with no gaps, and the worker keeps them updated."
      },
      guess: {
        it: "mercati di partenza SOL, BTC ed ETH; 12 mesi di storico; per Solana una fonte di dati come GeckoTerminal o Birdeye. Da scegliere all'inizio della fase.",
        en: "starting markets SOL, BTC and ETH; 12 months of history; for Solana a data source such as GeckoTerminal or Birdeye. To be chosen at the start of the phase."
      }
    },
    {
      title: { it: "Motore di backtest", en: "Backtest engine" },
      goal: {
        it: "Provare qualsiasi strategia sui dati del passato con costi realistici e leggere risultati di cui ci si può fidare.",
        en: "Test any strategy on past data with realistic costs and get results we can trust."
      },
      tasks: [
        { it: "Livelli comuni a tutte le strategie: rischio, dimensionamento, esecuzione simulata, portafoglio", en: "Layers shared by all strategies: risk, sizing, simulated execution, portfolio" },
        { it: "Costi veri nel calcolo: commissioni, finanziamento dei perpetui, slittamento del prezzo", en: "Real costs in the calculation: fees, perpetual funding, slippage" },
        { it: "Long e short con leva e prezzo di liquidazione (ripreso dal vecchio progetto), leva massima 2x-3x", en: "Long and short with leverage and liquidation price (from the old project), max leverage 2x-3x" },
        { it: "Metriche per operazione: profitto netto, durata, massimo guadagno e massima perdita non realizzati", en: "Per-trade metrics: net profit, duration, max unrealised gain and loss" },
        { it: "Report: guadagno, calo massimo (drawdown), operazioni vinte, perse e liquidate, grafico del saldo", en: "Report: return, max drawdown, winning, losing and liquidated trades, equity chart" },
        { it: "Registro di ogni decisione con il motivo", en: "Log of every decision with its reason" },
        { it: "Portare la vecchia strategia a pattern come prima strategia di prova", en: "Port the old pattern strategy as the first test strategy" },
        { it: "Ritestare la strategia a pattern con commissioni e leva bassa", en: "Retest the pattern strategy with fees and low leverage" }
      ],
      exit: {
        it: "Lanciamo un backtest della strategia a pattern su 12 mesi, con costi e leva 2x-3x, e otteniamo un report completo. Il risultato può anche essere negativo: conta che sia affidabile.",
        en: "We run a 12-month backtest of the pattern strategy, with costs and 2x-3x leverage, and get a full report. The result may be negative: what matters is that it is reliable."
      }
    },
    {
      title: { it: "Utenti, portafogli e ruoli", en: "Users, portfolios and roles" },
      goal: {
        it: "Più utenti, ognuno con i suoi portafogli, completamente separati tra loro.",
        en: "Several users, each with their own portfolios, fully separated from each other."
      },
      tasks: [
        { it: "Accesso con credenziali e tre ruoli: amministratore, utente, osservatore in sola lettura", en: "Login and three roles: administrator, user, read-only observer" },
        { it: "Portafogli simulati: nome, capitale, una o più strategie con la loro quota di capitale", en: "Simulated portfolios: name, capital, one or more strategies with their share of capital" },
        { it: "Limiti di rischio per portafoglio: perdita massima giornaliera, leva, posizioni aperte", en: "Risk limits per portfolio: max daily loss, leverage, open positions" },
        { it: "Invito di un osservatore su un portafoglio", en: "Invite an observer to a portfolio" },
        { it: "Separazione totale: nessun utente vede i dati di un altro", en: "Full separation: no user sees another user's data" },
        { it: "Risultato netto di ogni operazione salvato per utente (servirà per la percentuale sulle vincite)", en: "Net result of every trade stored per user (needed later for the cut on winning trades)" }
      ],
      exit: {
        it: "Due utenti di prova creano i loro portafogli simulati e nessuno dei due vede quelli dell'altro; un osservatore vede solo il portafoglio a cui è invitato.",
        en: "Two test users create their simulated portfolios and neither sees the other's; an observer sees only the portfolio they were invited to."
      }
    },
    {
      title: { it: "Dashboard web", en: "Web dashboard" },
      goal: {
        it: "Vedere e comandare tutto dal browser, senza toccare il codice.",
        en: "See and control everything from the browser, without touching the code."
      },
      tasks: [
        { it: "Mercato: prezzi e grafici delle criptovalute osservate", en: "Market: prices and charts of the watched cryptocurrencies" },
        { it: "Backtest: lanciarne uno scegliendo strategia, mercato e periodo, e leggerne il report", en: "Backtest: run one by choosing strategy, market and period, and read its report" },
        { it: "Portafogli: saldo, posizioni aperte, storico operazioni, andamento, risultati per strategia", en: "Portfolios: balance, open positions, trade history, performance, results per strategy" },
        { it: "Registro delle decisioni e degli ordini", en: "Log of decisions and orders" },
        { it: "Pagine di amministrazione: utenti e strategie disponibili", en: "Admin pages: users and available strategies" }
      ],
      exit: {
        it: "Un utente fa tutto il percorso dal browser: crea un portafoglio, lancia un backtest e ne legge i risultati.",
        en: "A user does the whole journey from the browser: creates a portfolio, runs a backtest and reads its results."
      }
    },
    {
      status: "paused",
      title: { it: "Server online", en: "Server online" },
      goal: {
        it: "Mettere l'app su un server in Europa che si aggiorna da solo a ogni modifica. In pausa per scelta: le fasi da 1 a 6 si sviluppano e si provano in locale con Docker, e il server torna in agenda prima della simulazione 24 ore su 24.",
        en: "Put the app on a server in Europe that updates itself on every change. On hold by choice: phases 1 to 6 are built and tested locally with Docker, and the server comes back before the 24/7 simulation."
      },
      tasks: [
        { s: "done", it: "Deploy automatico a ogni merge su <code>main</code> già pronto: si attiva da solo quando il server è configurato", en: "Automatic deploy on every merge to <code>main</code> already in place: it turns on by itself once the server is configured" },
        { it: "Comprare e preparare il VPS in Europa seguendo <a href=\"https://github.com/pittalavito/trader-slave-v2/blob/main/docs/server.md\">la guida del server</a>", en: "Buy and set up the VPS in Europe following <a href=\"https://github.com/pittalavito/trader-slave-v2/blob/main/docs/server.md\">the server guide</a> (in Italian)" },
        { it: "Aggiungere su GitHub i secret <code>VPS_HOST</code>, <code>VPS_USER</code> e <code>VPS_SSH_KEY</code>", en: "Add the <code>VPS_HOST</code>, <code>VPS_USER</code> and <code>VPS_SSH_KEY</code> secrets on GitHub" },
        { it: "Dominio e HTTPS (facoltativo ma consigliato)", en: "Domain and HTTPS (optional but recommended)" },
        { it: "Backup automatico giornaliero del database", en: "Automatic daily database backup" }
      ],
      exit: {
        it: "Un merge su <code>main</code> aggiorna il server da solo e la pagina dell'app risponde con lo stato dell'API \"ok\".",
        en: "A merge to <code>main</code> updates the server by itself and the app page shows the API status \"ok\"."
      },
    },
    {
      title: { it: "Simulazione 24 ore su 24 (paper trading)", en: "24/7 simulation (paper trading)" },
      goal: {
        it: "Le strategie girano sui prezzi reali di oggi, sempre accese, senza mandare ordini veri.",
        en: "Strategies run on today's real prices, always on, without sending real orders."
      },
      tasks: [
        { it: "Il worker esegue ogni strategia attiva alla chiusura di ogni candela del suo blocco (veloce, medio, lento)", en: "The worker runs each active strategy at the close of every candle of its block (fast, medium, slow)" },
        { it: "Più strategie nello stesso portafoglio, ognuna con la sua quota di capitale", en: "Several strategies in the same portfolio, each with its share of capital" },
        { it: "Freni che nessuna strategia può scavalcare: stop loss obbligatorio, perdita massima giornaliera, posizioni massime", en: "Brakes no strategy can override: mandatory stop loss, max daily loss, max positions" },
        { it: "Pulsante di emergenza: chiude tutto e ferma tutte le strategie", en: "Emergency button: closes everything and stops all strategies" },
        { it: "Avvio, pausa, stop e riconfigurazione di ogni strategia dalla dashboard", en: "Start, pause, stop and reconfigure each strategy from the dashboard" },
        { it: "Confronto tra simulazione e backtest sullo stesso periodo", en: "Compare simulation and backtest over the same period" },
        { it: "Accorgersi di connessione persa o dati fermi", en: "Detect lost connections or stale data" }
      ],
      exit: {
        it: "La strategia a pattern gira in simulazione per una settimana intera senza interruzioni e i suoi risultati sono coerenti con il backtest dello stesso periodo.",
        en: "The pattern strategy runs in simulation for a full week without interruptions and its results match the backtest of the same period."
      }
    },
    {
      title: { it: "Notifiche Telegram", en: "Telegram notifications" },
      goal: {
        it: "Sapere cosa succede senza aprire la dashboard.",
        en: "Know what is happening without opening the dashboard."
      },
      tasks: [
        { it: "Bot Telegram collegato a ogni utente", en: "Telegram bot linked to each user" },
        { it: "Avvisi immediati: operazione aperta o chiusa, stop scattato, limite di rischio raggiunto, errore, connessione persa", en: "Instant alerts: trade opened or closed, stop hit, risk limit reached, error, connection lost" },
        { it: "Riepilogo giornaliero per portafoglio", en: "Daily summary per portfolio" }
      ],
      exit: {
        it: "Ogni evento importante della simulazione arriva su Telegram entro pochi secondi, e ogni giorno arriva il riepilogo.",
        en: "Every important simulation event reaches Telegram within seconds, and the summary arrives every day."
      },
      guess: {
        it: "nella specifica le notifiche sono previste per la seconda versione; le metto prima dei soldi veri perché l'avviso di connessione persa serve quando ci sono posizioni aperte.",
        en: "the spec puts notifications in the second version; they come before real money here because the lost-connection alert matters when positions are open."
      }
    },
    {
      title: { it: "Regole delle strategie A e B", en: "Rules for strategies A and B" },
      goal: {
        it: "Definire le regole di entrata e uscita delle due strategie e dimostrare con i dati che funzionano.",
        en: "Define the entry and exit rules of both strategies and prove with data that they work."
      },
      tasks: [
        { it: "Strategia B (futures perpetui Kraken, long e short): regole di entrata, uscita, stop loss e take profit", en: "Strategy B (Kraken perpetual futures, long and short): entry, exit, stop loss and take profit rules" },
        { it: "Strategia A (spot su DEX Solana): regole di entrata, uscita, stop loss e take profit", en: "Strategy A (spot on a Solana DEX): entry, exit, stop loss and take profit rules" },
        { it: "Scegliere i token su cui opera ciascuna", en: "Choose the tokens each one trades" },
        { it: "Backtest su 12 mesi con costi, poi simulazione sui prezzi reali", en: "12-month backtest with costs, then simulation on real prices" }
      ],
      exit: {
        it: "Ogni strategia ha un backtest positivo al netto dei costi e un periodo di simulazione con risultati coerenti, e Vito decide di passarla ai soldi veri.",
        en: "Each strategy has a positive backtest net of costs and a simulation period with consistent results, and Vito decides to move it to real money."
      },
      guess: {
        it: "le regole sono rimandate a questa fase; si parte dalla strategia a pattern e da strategie note. Durata minima della simulazione proposta: 4 settimane. Questa fase può iniziare in parallelo, appena il backtest è pronto.",
        en: "the rules are deferred to this phase; we start from the pattern strategy and well-known strategies. Proposed minimum simulation length: 4 weeks. This phase can start in parallel as soon as the backtest is ready."
      }
    },
    {
      title: { it: "Rafforzare la sicurezza", en: "Security hardening" },
      goal: {
        it: "Prima di mettere soldi veri, alzare il livello di sicurezza e chiudere i punti deboli raccolti strada facendo.",
        en: "Before real money goes in, raise the security level and close the weak spots collected along the way."
      },
      tasks: [
        { it: "Spostare le chiavi API e dei wallet dal database cifrato a una cassaforte dedicata (per esempio Vault o un KMS)", en: "Move API and wallet keys from the encrypted database to a dedicated vault (for example Vault or a KMS)" },
        { it: "Rotazione periodica delle chiavi e della chiave di cifratura", en: "Periodic rotation of keys and of the encryption key" },
        { it: "Verifica in due passaggi (2FA) per il login", en: "Two-factor authentication (2FA) for login" },
        { it: "Limiti alle richieste e blocco dopo troppi tentativi di accesso", en: "Rate limits and lockout after too many login attempts" },
        { it: "Registro di chi fa cosa (accessi, modifiche, comandi al motore)", en: "Audit log of who does what (logins, changes, engine commands)" },
        { it: "Backup cifrati e prova di ripristino", en: "Encrypted backups and a restore test" },
        { it: "Controllo automatico delle dipendenze con vulnerabilità note", en: "Automatic check for dependencies with known vulnerabilities" },
        { it: "Chiudere i punti di sicurezza annotati durante lo sviluppo", en: "Close the security items noted during development" }
      ],
      exit: {
        it: "Tutte le attività sono fatte e non restano punti di sicurezza aperti prima del primo euro vero.",
        en: "All tasks are done and no security items remain open before the first real euro."
      },
      guess: {
        it: "per ora le chiavi stanno cifrate nel database (deciso). Ogni punto di sicurezza trovato durante lo sviluppo si aggiunge a questa fase.",
        en: "for now keys are stored encrypted in the database (decided). Every security issue found during development gets added to this phase."
      }
    },
    {
      title: { it: "Soldi veri: strategia B su Kraken", en: "Real money: strategy B on Kraken" },
      goal: {
        it: "La strategia B opera con soldi veri sul conto Kraken, con un capitale piccolo e tutti i freni attivi.",
        en: "Strategy B trades real money on the Kraken account, with small capital and all brakes on."
      },
      tasks: [
        { it: "Verificare i requisiti Kraken per i clienti italiani e i tassi di finanziamento reali", en: "Check Kraken's requirements for Italian clients and the real funding rates" },
        { it: "Collegare il conto Kraken del portafoglio con chiavi API cifrate, senza permesso di prelievo e limitate all'IP del server", en: "Connect the portfolio's Kraken account with encrypted API keys, no withdrawal permission, restricted to the server IP" },
        { it: "Livello di esecuzione reale: ordini, stop sul conto, riconciliazione tra posizioni dell'app e del conto", en: "Real execution layer: orders, stops on the account, reconciliation between app and account positions" },
        { it: "Leva bloccata a 2x-3x nell'app", en: "Leverage capped at 2x-3x in the app" },
        { it: "Passaggio da simulato a reale sempre manuale, con conferma esplicita", en: "Switching from simulated to real is always manual, with explicit confirmation" },
        { it: "Partire con un capitale piccolo e confrontare ogni settimana con la simulazione", en: "Start with small capital and compare weekly against the simulation" }
      ],
      exit: {
        it: "La strategia B gira per un mese con soldi veri, senza differenze inspiegate tra i conti dell'app e quelli di Kraken.",
        en: "Strategy B runs for a month with real money, with no unexplained differences between the app's books and Kraken's."
      },
      guess: {
        it: "metto Kraken prima di Solana perché le chiavi API si possono limitare all'IP del server e gli ordini sono più semplici da gestire. L'ordine si può invertire.",
        en: "Kraken comes before Solana because API keys can be restricted to the server IP and orders are simpler to manage. The order can be swapped."
      }
    },
    {
      title: { it: "Soldi veri: strategia A su Solana", en: "Real money: strategy A on Solana" },
      goal: {
        it: "La strategia A compra e vende spot su un DEX Solana dal wallet dedicato del portafoglio.",
        en: "Strategy A buys and sells spot on a Solana DEX from the portfolio's dedicated wallet."
      },
      tasks: [
        { it: "Wallet Solana dedicato con dentro solo il capitale della strategia", en: "Dedicated Solana wallet holding only the strategy's capital" },
        { it: "Custodia sicura della chiave del wallet sul server", en: "Secure storage of the wallet key on the server" },
        { it: "Livello di esecuzione: scambi sul DEX con limite di slittamento, conferma delle transazioni, gestione dei fallimenti", en: "Execution layer: DEX swaps with slippage limit, transaction confirmation, failure handling" },
        { it: "Riconciliazione tra saldo del wallet e conti dell'app", en: "Reconciliation between wallet balance and the app's books" },
        { it: "Partire con un capitale piccolo", en: "Start with small capital" }
      ],
      exit: {
        it: "La strategia A gira per un mese con soldi veri e il saldo del wallet corrisponde sempre a quello dell'app.",
        en: "Strategy A runs for a month with real money and the wallet balance always matches the app's."
      },
      guess: {
        it: "gli scambi passano da un aggregatore come Jupiter, che trova il prezzo migliore tra i DEX Solana. Da decidere all'inizio della fase.",
        en: "swaps go through an aggregator such as Jupiter, which finds the best price across Solana DEXs. To be decided at the start of the phase."
      }
    },
    {
      title: { it: "Apertura a utenti esterni e abbonamenti", en: "External users and subscriptions" },
      goal: {
        it: "Far usare l'app a utenti paganti, ognuno sui propri conti.",
        en: "Let paying users use the app, each on their own accounts."
      },
      tasks: [
        { it: "Verifica con un consulente: se la percentuale sulle vincite rende l'app un'attività finanziaria regolamentata", en: "Check with an advisor whether the cut on winnings makes the app a regulated financial activity" },
        { it: "Termini di servizio e privacy", en: "Terms of service and privacy policy" },
        { it: "Registrazione e collegamento guidato dei conti per i nuovi utenti", en: "Sign-up and guided account connection for new users" },
        { it: "Abbonamento mensile con pagamento online", en: "Monthly subscription with online payment" },
        { it: "Percentuale sulle operazioni vincenti, quando l'app è completamente automatica (calcolo da definire)", en: "Cut on winning trades, once the app is fully automatic (calculation to be defined)" },
        { it: "Strumenti di assistenza per l'amministratore", en: "Support tools for the administrator" }
      ],
      exit: {
        it: "Un utente esterno si registra, collega i suoi conti, paga l'abbonamento e usa l'app senza il nostro aiuto.",
        en: "An external user signs up, connects their accounts, pays the subscription and uses the app without our help."
      }
    }
  ],

  deferred: [
    { it: "Regole di entrata e uscita delle strategie: si definiscono nella fase 10.", en: "Strategy entry and exit rules: defined in phase 10." },
    { it: "Come si calcola la percentuale sulle vincite: nella fase 14, dopo la verifica legale.", en: "How the cut on winnings is calculated: in phase 14, after the legal check." },
    { it: "Su quali token opera ogni strategia: dopo i test della fase 10.", en: "Which tokens each strategy trades: after the tests in phase 10." }
  ],

  outside: [
    { it: "Strategie basate su intelligenza artificiale o notizie.", en: "Strategies based on artificial intelligence or news." },
    { it: "App per smartphone: basta la dashboard da browser.", en: "Smartphone app: the browser dashboard is enough." },
    { it: "Exchange e wallet oltre a Kraken e Solana.", en: "Exchanges and wallets other than Kraken and Solana." },
    { it: "Mercati diversi dalle criptovalute.", en: "Markets other than cryptocurrencies." }
  ]
};
