from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import models, schemas
from .auth import current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="GTS Operations Hub",
    description="A learning-oriented mini enterprise infrastructure operations platform.",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    return (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/health")
def health():
    return {"status": "healthy", "service": "gts-operations-hub", "timestamp": datetime.now(timezone.utc)}

@app.get("/api/v1/overview")
def overview(db: Session = Depends(get_db), user=Depends(current_user)):
    total = db.scalar(select(func.count(models.Asset.id))) or 0
    healthy = db.scalar(select(func.count(models.Asset.id)).where(models.Asset.status == "healthy")) or 0
    open_incidents = db.scalar(select(func.count(models.Incident.id)).where(models.Incident.status == "open")) or 0
    return {"total_assets": total, "healthy_assets": healthy, "unhealthy_assets": total-healthy, "open_incidents": open_incidents}

@app.get("/api/v1/assets", response_model=list[schemas.AssetOut])
def list_assets(asset_type: str | None = None, environment: str | None = None,
                db: Session = Depends(get_db), user=Depends(current_user)):
    stmt = select(models.Asset).order_by(models.Asset.id.desc())
    if asset_type:
        stmt = stmt.where(models.Asset.asset_type == asset_type)
    if environment:
        stmt = stmt.where(models.Asset.environment == environment)
    return db.scalars(stmt).all()

@app.post("/api/v1/assets", response_model=schemas.AssetOut, status_code=201)
def create_asset(payload: schemas.AssetCreate, db: Session = Depends(get_db), user=Depends(current_user)):
    if db.scalar(select(models.Asset).where(models.Asset.name == payload.name)):
        raise HTTPException(409, "An asset with this name already exists")
    asset = models.Asset(**payload.model_dump())
    db.add(asset); db.commit(); db.refresh(asset)
    return asset

@app.get("/api/v1/assets/{asset_id}", response_model=schemas.AssetOut)
def get_asset(asset_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    asset = db.get(models.Asset, asset_id)
    if not asset: raise HTTPException(404, "Asset not found")
    return asset

@app.patch("/api/v1/assets/{asset_id}", response_model=schemas.AssetOut)
def update_asset(asset_id: int, payload: schemas.AssetUpdate, db: Session = Depends(get_db), user=Depends(current_user)):
    asset = db.get(models.Asset, asset_id)
    if not asset: raise HTTPException(404, "Asset not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset, key, value)
    db.commit(); db.refresh(asset)
    return asset

@app.delete("/api/v1/assets/{asset_id}", status_code=204)
def delete_asset(asset_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    asset = db.get(models.Asset, asset_id)
    if not asset: raise HTTPException(404, "Asset not found")
    db.delete(asset); db.commit()
    return None

@app.get("/api/v1/dependencies", response_model=list[schemas.DependencyOut])
def list_dependencies(db: Session = Depends(get_db), user=Depends(current_user)):
    return db.scalars(select(models.Dependency).order_by(models.Dependency.id)).all()

@app.post("/api/v1/dependencies", response_model=schemas.DependencyOut, status_code=201)
def create_dependency(payload: schemas.DependencyCreate, db: Session = Depends(get_db), user=Depends(current_user)):
    if payload.source_id == payload.target_id: raise HTTPException(400, "An asset cannot depend on itself")
    if not db.get(models.Asset, payload.source_id) or not db.get(models.Asset, payload.target_id):
        raise HTTPException(404, "Both source and target assets must exist")
    dep = models.Dependency(**payload.model_dump())
    db.add(dep); db.commit(); db.refresh(dep)
    return dep

@app.get("/api/v1/incidents", response_model=list[schemas.IncidentOut])
def list_incidents(status: str | None = None, db: Session = Depends(get_db), user=Depends(current_user)):
    stmt = select(models.Incident).order_by(models.Incident.created_at.desc())
    if status: stmt = stmt.where(models.Incident.status == status)
    return db.scalars(stmt).all()

@app.post("/api/v1/incidents", response_model=schemas.IncidentOut, status_code=201)
def create_incident(payload: schemas.IncidentCreate, db: Session = Depends(get_db), user=Depends(current_user)):
    if payload.asset_id and not db.get(models.Asset, payload.asset_id):
        raise HTTPException(404, "Asset not found")
    incident = models.Incident(**payload.model_dump())
    db.add(incident); db.commit(); db.refresh(incident)
    return incident

@app.post("/api/v1/incidents/{incident_id}/resolve", response_model=schemas.IncidentOut)
def resolve_incident(incident_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    incident = db.get(models.Incident, incident_id)
    if not incident: raise HTTPException(404, "Incident not found")
    incident.status = "resolved"
    incident.resolved_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(incident)
    return incident

@app.post("/api/v1/demo/seed")
def seed_demo(db: Session = Depends(get_db), user=Depends(current_user)):
    """Idempotently add sample assets and an incident for a portfolio demo."""
    samples = [
        ("gts-api", "application", "development", "gts-api.local", "10.10.0.10", "platform-team", "healthy", "FastAPI service"),
        ("gts-postgres", "database", "development", "postgres.local", "10.10.0.20", "database-team", "healthy", "PostgreSQL asset"),
        ("identity-service", "identity", "development", "keycloak.local", "10.10.0.30", "security-team", "degraded", "Keycloak identity provider"),
        ("metrics-agent", "monitoring", "development", "metrics.local", "10.10.0.40", "sre-team", "healthy", "Demo monitoring component"),
    ]
    by_name = {}
    for row in samples:
        asset = db.scalar(select(models.Asset).where(models.Asset.name == row[0]))
        if not asset:
            asset = models.Asset(name=row[0], asset_type=row[1], environment=row[2], hostname=row[3],
                                 ip_address=row[4], owner=row[5], status=row[6], description=row[7])
            db.add(asset); db.flush()
        by_name[row[0]] = asset
    if not db.scalar(select(models.Dependency).where(
        models.Dependency.source_id == by_name["gts-api"].id,
        models.Dependency.target_id == by_name["gts-postgres"].id)):
        db.add(models.Dependency(source_id=by_name["gts-api"].id, target_id=by_name["gts-postgres"].id))
    if not db.scalar(select(models.Incident).where(models.Incident.title == "Identity service degraded", models.Incident.status == "open")):
        db.add(models.Incident(asset_id=by_name["identity-service"].id, title="Identity service degraded",
                               severity="medium", details="Seeded demonstration incident."))
    db.commit()
    return {"message": "Demo data is ready", "assets": len(samples)}

@app.get("/api/v1/metrics", response_class=PlainTextResponse)
def metrics(db: Session = Depends(get_db), user=Depends(current_user)):
    """Prometheus-compatible basic metrics."""
    total = db.scalar(select(func.count(models.Asset.id))) or 0
    healthy = db.scalar(select(func.count(models.Asset.id)).where(models.Asset.status == "healthy")) or 0
    open_incidents = db.scalar(select(func.count(models.Incident.id)).where(models.Incident.status == "open")) or 0
    return (
        "# HELP gts_assets_total Total registered configuration items\n"
        "# TYPE gts_assets_total gauge\n"
        f"gts_assets_total {total}\n"
        "# HELP gts_assets_healthy Healthy configuration items\n"
        "# TYPE gts_assets_healthy gauge\n"
        f"gts_assets_healthy {healthy}\n"
        "# HELP gts_incidents_open Open incidents\n"
        "# TYPE gts_incidents_open gauge\n"
        f"gts_incidents_open {open_incidents}\n"
    )


@app.get("/api/v1/system")
def system_info():
    """Show the deployment mode without exposing credentials."""
    import os
    return {"runtime": "native-python", "database": "sqlite" if engine.dialect.name == "sqlite" else "postgresql",
            "authentication_enabled": os.getenv("AUTH_ENABLED", "false").lower() == "true"}
