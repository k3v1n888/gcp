# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func, Boolean
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/cyberdb")
Base = declarative_base()

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
    # Relationship to automation logs
    automation_actions = relationship("AutomationLog", back_populates="threat")

class SystemSettings(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True)
    alert_severity = Column(String, default="critical")

class CorrelatedThreat(Base):
    # ... (This model is unchanged)
    pass

# --- NEW: Table to log automated SOAR actions ---
class AutomationLog(Base):
    __tablename__ = "automation_logs"
    id = Column(Integer, primary_key=True)
    threat_id = Column(Integer, ForeignKey("threat_logs.id"))
    action_type = Column(String) # e.g., "IP_BLOCK_SUCCESS"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(Text)
    threat = relationship("ThreatLog", back_populates="automation_actions")

# --- NEW: Table to log user activities for UEBA ---
class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String) # e.g., "user_login", "view_threat_details"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(Text, nullable=True)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
