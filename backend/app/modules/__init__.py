"""Business logic, split by area.

Every area has the same shape: `models.py` (tables), `schemas.py` (API input and
output, Pydantic), `service.py` (logic), `repository.py` (queries).
Endpoints in `app.api` only call services.
"""
