# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func, Boolean, Table, JSON
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/cyberdb")
Base = declarative_base()

incident_threat_association = Table('incident_threat_association', Base.metadata,
    Column('incident_id', Integer, ForeignKey('security_incidents.id'), primary_key=True),
    Column('threat_log_id', Integer, ForeignKey('threat_logs.id'), primary_key=True)
)

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="tenant")
    threats = relationship("ThreatLog", back_populates="tenant")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(String, default="viewer")
    status = Column(String, default="active")
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", back_populates="users")

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ThreatLog(Base):
    __tablename__ = "threat_logs"
    id = Column(Integer, primary_key=True)
    ip = Column(String)
    threat = Column(Text)
    source = Column(String)
    severity = Column(String, default="unknown")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", back_populates="threats")
    ip_reputation_score = Column(Integer, nullable=True)
    cve_id = Column(String, nullable=True)
    is_anomaly = Column(Boolean, default=False)
    automation_actions = relationship("AutomationLog", back_populates="threat")
    incidents = relationship("SecurityIncident", secondary=incident_threat_association, back_populates="threat_logs")

class SystemSettings(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True)
    alert_severity = Column(String, default="critical")

class CorrelatedThreat(Base):
    __tablename__ = "correlated_threats"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(Text, nullable=True)
    cve_id = Column(String, nullable=True)
    risk_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tenant_id = Column(Integer, ForeignKey("tenants.id"))

class AutomationLog(Base):
    __tablename__ = "automation_logs"
    id = Column(Integer, primary_key=True)
    threat_id = Column(Integer, ForeignKey("threat_logs.id"))
    action_type = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(Text)
    threat = relationship("ThreatLog", back_populates="automation_actions")

class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(Text, nullable=True)

class SecurityIncident(Base):
    __tablename__ = "security_incidents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    status = Column(String, default="open")
    severity = Column(String)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    threat_logs = relationship("ThreatLog", secondary=incident_threat_association, back_populates="incidents")

# --- NEW: Table to log threat hunting results ---
class ThreatHunt(Base):
    __tablename__ = "threat_hunts"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    query = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    results = Column(JSON, nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)