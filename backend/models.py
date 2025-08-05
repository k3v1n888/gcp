# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/cyberdb")
Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Remove the problematic relationship for now

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

class ThreatLog(Base):
    __tablename__ = "threat_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    ip = Column(String(45), nullable=False, index=True)
    threat_type = Column(String(100), nullable=False)
    threat = Column(String(500))
    severity = Column(String(20), nullable=False, default="medium")
    description = Column(Text)
    cve_id = Column(String(20), index=True)
    cvss_score = Column(Float)
    source = Column(String(50), default="api")
    ip_reputation_score = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)
    
    # Fix timestamp with proper default
    timestamp = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=func.now(),
        server_default=func.now()
    )

class CorrelatedThreat(Base):
    __tablename__ = "correlated_threats"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())

class AutomationLog(Base):
    __tablename__ = "automation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    threat_id = Column(Integer, ForeignKey("threat_logs.id"))
    action = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now())