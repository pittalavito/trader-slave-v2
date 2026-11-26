"""The part shared by the whole backend.

No file in here imports from `app.modules`, `app.clients` or `app.engine`:
the core depends on nothing, everything else depends on the core.
"""
