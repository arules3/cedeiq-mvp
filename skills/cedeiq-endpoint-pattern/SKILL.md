---
name: cedeiq-endpoint-pattern
description: Use when adding a new FastAPI endpoint to CedeIQ. Encodes the project's established pattern of router + Pydantic schema + service-layer call + audit logging, so new endpoints stay consistent with existing ones (treaties, policies, cessions).
---

# CedeIQ Endpoint Pattern

Every endpoint in this project follows the same shape. When asked to add a new
one, follow this pattern exactly rather than inventing a new structure.

## 1. Schema first (`app/schemas.py`)

Define a `<Thing>Create` Pydantic model for the request body and a
`<Thing>Out` model (usually `<Thing>Create` + `id` + `created_at`, with
`model_config = ConfigDict(from_attributes=True)`) for the response.

## 2. Router (`app/routers/<thing>.py`)

- `router = APIRouter(prefix="/<things>", tags=["<things>"])`
- Route functions take `db: Session = Depends(get_db)` and a Pydantic schema
  as the request body — never a raw `dict`.
- **Never put business logic in the router.** If the endpoint needs
  calculation or decision logic, call into `app/services/`, don't inline it.
  (See CLAUDE.md steering rule 1.)

## 3. Service layer, if the endpoint does more than a plain insert

Business logic — like the rules engine's treaty matching — lives in
`app/services/`. Keep these functions pure where possible (no DB calls
inside), because that's what made `rules_engine.py` unit-testable without a
database (see `backend/tests/test_rules_engine.py`).

## 4. Audit logging, if the endpoint makes an automated decision

Any endpoint that has the system decide something on the user's behalf
(not just a plain CRUD create) must write an `AuditLog` row: what fired,
what went in, what came out. `routers/cessions.py`'s `run_cessions()` is
the reference example.

## 5. Register the router

Add `app.include_router(<thing>.router)` in `app/main.py`.

## 6. Test it

Add a test in `backend/tests/` if the endpoint has any decision logic
(matching, calculation, validation beyond Pydantic). Pure CRUD endpoints
can skip dedicated tests for MVP scope.

## Example of this pattern already in use

`app/routers/policies.py`'s `upload_policies()` — schema-validated per-row,
service-free (it's a straightforward bulk insert), with per-row error
collection instead of a single try/except around the whole batch.
