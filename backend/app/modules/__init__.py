"""La logica dell'app, divisa per area.

Ogni area ha la stessa forma: `models.py` (tabelle), `schemas.py` (dati in
entrata e uscita dall'API, Pydantic), `service.py` (logica), `repository.py`
(query). Gli endpoint in `app.api` chiamano solo i service.
"""
