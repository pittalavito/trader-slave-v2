"""Processo del motore dei bot, separato dall'API.

Per ora non ci sono bot configurati: il processo resta acceso e registra
un battito a ogni ciclo, così si può verificare che il deploy funzioni.
"""

import logging
import signal
import time

from app.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("worker")

_running = True


def _stop(*_: object) -> None:
    global _running
    _running = False


def main() -> None:
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    tick = get_settings().engine_tick_seconds
    log.info("Motore avviato, un ciclo ogni %s secondi", tick)
    while _running:
        # Qui il motore eseguirà Engine.run_cycle() per ogni bot attivo.
        log.info("Ciclo del motore: nessun bot attivo")
        for _ in range(tick):
            if not _running:
                break
            time.sleep(1)
    log.info("Motore fermato")


if __name__ == "__main__":
    main()
