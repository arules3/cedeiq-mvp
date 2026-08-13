from fastapi import FastAPI

from app.db import Base, engine
from app import models  # noqa: F401 - import so SQLAlchemy registers all tables
from app.routers import treaties, policies, cessions, audit_log, dashboard

app = FastAPI(title="CedeIQ API", version="0.1.0")

# MVP simplicity: create tables on startup instead of Alembic migrations.
# Revisit with proper migrations if this ever goes past MVP.
Base.metadata.create_all(bind=engine)

app.include_router(treaties.router)
app.include_router(policies.router)
app.include_router(cessions.router)
app.include_router(audit_log.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "cedeiq-backend"}
