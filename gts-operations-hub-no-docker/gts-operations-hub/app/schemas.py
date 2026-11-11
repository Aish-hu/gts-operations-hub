from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class AssetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    asset_type: str = Field(min_length=2, max_length=40)
    environment: str = "development"
    hostname: str | None = None
    ip_address: str | None = None
    owner: str = "platform-team"
    status: str = "healthy"
    description: str | None = None

class AssetUpdate(BaseModel):
    name: str | None = None
    asset_type: str | None = None
    environment: str | None = None
    hostname: str | None = None
    ip_address: str | None = None
    owner: str | None = None
    status: str | None = None
    description: str | None = None

class AssetOut(AssetCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class DependencyCreate(BaseModel):
    source_id: int
    target_id: int
    relationship_type: str = "depends_on"

class DependencyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source_id: int
    target_id: int
    relationship_type: str

class IncidentCreate(BaseModel):
    asset_id: int | None = None
    title: str
    severity: str = "medium"
    details: str | None = None

class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_id: int | None
    title: str
    severity: str
    status: str
    details: str | None
    created_at: datetime
    resolved_at: datetime | None
