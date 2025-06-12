from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    role = Column(String, default="viewer")  # viewer, analyst, admin
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", back_populates="users")
    
    def as_dict(self):
       """Converts the object to a dictionary."""
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ThreatLog(Base):
    __tablename__ = "threat_logs"
    id = Column(Integer, primary_key=True)
    ip = Column(String)
    threat = Column(Text)
    source = Column(String)
    severity = Column(String, default="unknown")
    timestamp = Column(DateTime, default=func.now())
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    tenant = relationship("Tenant", back_populates="threats")

class SystemSettings(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True)
    alert_severity = Column(String, default="critical")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
