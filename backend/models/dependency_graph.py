# backend/models/dependency_graph.py
from sqlalchemy import Column, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from .database import Base

class DependencyGraph(Base):
    """
    Minimal dependency graph storage.
    Adjust fields later if you need edges/nodes/metadata.
    """
    __tablename__ = "dependency_graphs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # generic JSON payload for nodes/edges/etc.
    payload = Column(JSON, nullable=False, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

