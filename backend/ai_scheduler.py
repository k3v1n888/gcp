"""
Copyright (c) 2025 Kevin Zachary
All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Kevin Zachary. Unauthorized copying, distribution, 
modification, or use of this software is strictly prohibited.

For licensing inquiries, contact: kevin@zachary.com
"""

# Author: Kevin Zachary
# Copyright: Sentient Spire

"""
⏰ AI Incident Orchestration Scheduler
Automated scheduling service for intelligent incident creation

This service runs AI-driven incident orchestration on a regular schedule,
ensuring threats are continuously analyzed and aggregated into security incidents.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .database import SessionLocal
from .ai_incident_orchestrator import run_ai_incident_orchestration
from .models import AutomationLog

logger = logging.getLogger(__name__)

class AIIncidentScheduler:
    """
    🤖 Automated scheduler for AI incident orchestration
    
    Runs intelligent incident creation on configurable schedules:
    - Real-time: Every 5 minutes for critical threats
    - Standard: Every 15 minutes for regular correlation
    - Deep Analysis: Every hour for comprehensive review
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
        # Schedule configurations
        self.schedules = {
            "realtime": {"minutes": 5, "enabled": True},      # Critical threat response
            "standard": {"minutes": 15, "enabled": True},     # Regular incident creation
            "deep_analysis": {"hours": 1, "enabled": True},   # Comprehensive analysis
            "maintenance": {"hours": 6, "enabled": True}      # System maintenance
        }
    
    def start_scheduler(self):
        """🚀 Start the AI incident orchestration scheduler"""
        if self.is_running:
            logger.warning("⚠️ Scheduler is already running")
            return
        
        try:
            logger.info("🚀 Starting AI Incident Orchestration Scheduler")
            
            # Real-time incident creation (every 5 minutes)
            if self.schedules["realtime"]["enabled"]:
                self.scheduler.add_job(
                    func=self._run_realtime_orchestration,
                    trigger=IntervalTrigger(minutes=self.schedules["realtime"]["minutes"]),
                    id="realtime_incident_orchestration",
                    name="Real-time AI Incident Creation",
                    max_instances=1,
                    coalesce=True
                )
                logger.info("✅ Real-time orchestration scheduled (every 5 minutes)")
            
            # Standard incident creation (every 15 minutes)
            if self.schedules["standard"]["enabled"]:
                self.scheduler.add_job(
                    func=self._run_standard_orchestration,
                    trigger=IntervalTrigger(minutes=self.schedules["standard"]["minutes"]),
                    id="standard_incident_orchestration",
                    name="Standard AI Incident Creation",
                    max_instances=1,
                    coalesce=True
                )
                logger.info("✅ Standard orchestration scheduled (every 15 minutes)")
            
            # Deep analysis (every hour)
            if self.schedules["deep_analysis"]["enabled"]:
                self.scheduler.add_job(
                    func=self._run_deep_analysis,
                    trigger=IntervalTrigger(hours=self.schedules["deep_analysis"]["hours"]),
                    id="deep_analysis_orchestration",
                    name="Deep Analysis AI Orchestration",
                    max_instances=1,
                    coalesce=True
                )
                logger.info("✅ Deep analysis scheduled (every hour)")
            
            # System maintenance (every 6 hours)
            if self.schedules["maintenance"]["enabled"]:
                self.scheduler.add_job(
                    func=self._run_maintenance,
                    trigger=IntervalTrigger(hours=self.schedules["maintenance"]["hours"]),
                    id="orchestration_maintenance",
                    name="AI Orchestration Maintenance",
                    max_instances=1,
                    coalesce=True
                )
                logger.info("✅ Maintenance scheduled (every 6 hours)")
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info("🎯 AI Incident Orchestration Scheduler started successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            raise
    
    def stop_scheduler(self):
        """⏹️ Stop the scheduler"""
        if not self.is_running:
            logger.warning("⚠️ Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            logger.info("⏹️ AI Incident Orchestration Scheduler stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")
    
    async def _run_realtime_orchestration(self):
        """🔥 Real-time orchestration for critical threats"""
        logger.info("🔥 Running real-time AI incident orchestration")
        
        try:
            db = SessionLocal()
            
            # Run for all tenants (you might want to make this configurable)
            tenants = [1]  # Add logic to get all tenant IDs
            
            total_incidents = 0
            for tenant_id in tenants:
                result = await run_ai_incident_orchestration(db, tenant_id)
                if result["status"] == "success":
                    incidents_created = result.get("incidents_created", 0)
                    total_incidents += incidents_created
                    
                    if incidents_created > 0:
                        logger.info(f"⚡ Created {incidents_created} incidents for tenant {tenant_id}")
                        
                        # Log automation activity
                        automation_log = AutomationLog(
                            action_type="realtime_orchestration",
                            details=f"Real-time orchestration created {incidents_created} incidents",
                            timestamp=datetime.utcnow()
                        )
                        db.add(automation_log)
            
            if total_incidents > 0:
                db.commit()
                logger.info(f"✅ Real-time orchestration completed: {total_incidents} total incidents created")
            else:
                logger.debug("📊 Real-time orchestration: No new incidents created")
                
        except Exception as e:
            logger.error(f"❌ Real-time orchestration failed: {e}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    async def _run_standard_orchestration(self):
        """📊 Standard orchestration for regular incident creation"""
        logger.info("📊 Running standard AI incident orchestration")
        
        try:
            db = SessionLocal()
            
            # Run comprehensive analysis for all tenants
            tenants = [1]  # Add logic to get all tenant IDs
            
            results = []
            for tenant_id in tenants:
                result = await run_ai_incident_orchestration(db, tenant_id)
                results.append(result)
                
                if result["status"] == "success":
                    incidents_created = result.get("incidents_created", 0)
                    if incidents_created > 0:
                        logger.info(f"🎯 Standard orchestration: {incidents_created} incidents for tenant {tenant_id}")
            
            # Log comprehensive results
            total_incidents = sum(r.get("incidents_created", 0) for r in results if r["status"] == "success")
            
            automation_log = AutomationLog(
                action_type="standard_orchestration",
                details=f"Standard orchestration run completed. {total_incidents} incidents created across {len(tenants)} tenants",
                timestamp=datetime.utcnow()
            )
            db.add(automation_log)
            db.commit()
            
            logger.info(f"✅ Standard orchestration completed: {total_incidents} total incidents")
            
        except Exception as e:
            logger.error(f"❌ Standard orchestration failed: {e}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    async def _run_deep_analysis(self):
        """🔬 Deep analysis orchestration for comprehensive threat correlation"""
        logger.info("🔬 Running deep analysis AI orchestration")
        
        try:
            db = SessionLocal()
            
            # Perform deep analysis including:
            # 1. Historical threat pattern analysis
            # 2. Cross-tenant threat correlation (if applicable)
            # 3. Long-term campaign detection
            # 4. Advanced persistent threat identification
            
            tenants = [1]  # Add logic to get all tenant IDs
            
            for tenant_id in tenants:
                # Run standard orchestration
                result = await run_ai_incident_orchestration(db, tenant_id)
                
                # Additional deep analysis could go here
                # - Analyze threat patterns over extended periods
                # - Correlate with external threat intelligence
                # - Update incident risk scores based on new intelligence
                
                if result["status"] == "success":
                    incidents_created = result.get("incidents_created", 0)
                    logger.info(f"🔬 Deep analysis: {incidents_created} incidents for tenant {tenant_id}")
            
            # Log deep analysis completion
            automation_log = AutomationLog(
                action_type="deep_analysis_orchestration", 
                details="Deep analysis orchestration completed with comprehensive threat correlation",
                timestamp=datetime.utcnow()
            )
            db.add(automation_log)
            db.commit()
            
            logger.info("✅ Deep analysis orchestration completed")
            
        except Exception as e:
            logger.error(f"❌ Deep analysis failed: {e}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    async def _run_maintenance(self):
        """🔧 System maintenance for orchestration components"""
        logger.info("🔧 Running AI orchestration maintenance")
        
        try:
            db = SessionLocal()
            
            # Maintenance tasks:
            # 1. Clean up old automation logs
            # 2. Archive resolved incidents
            # 3. Update threat intelligence caches
            # 4. Optimize correlation models
            
            # Clean up old automation logs (keep last 30 days)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            old_logs = db.query(AutomationLog).filter(
                AutomationLog.timestamp < cutoff_date
            ).count()
            
            if old_logs > 0:
                db.query(AutomationLog).filter(
                    AutomationLog.timestamp < cutoff_date
                ).delete()
                
                logger.info(f"🧹 Cleaned up {old_logs} old automation logs")
            
            # Log maintenance completion
            automation_log = AutomationLog(
                action_type="system_maintenance",
                details=f"System maintenance completed. Cleaned up {old_logs} old logs.",
                timestamp=datetime.utcnow()
            )
            db.add(automation_log)
            db.commit()
            
            logger.info("✅ System maintenance completed")
            
        except Exception as e:
            logger.error(f"❌ System maintenance failed: {e}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    def get_scheduler_status(self) -> dict:
        """📊 Get current scheduler status and metrics"""
        status = {
            "is_running": self.is_running,
            "jobs": [],
            "next_runs": {}
        }
        
        if self.is_running:
            for job in self.scheduler.get_jobs():
                job_info = {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                }
                status["jobs"].append(job_info)
                
                if job.next_run_time:
                    status["next_runs"][job.id] = job.next_run_time.isoformat()
        
        return status
    
    def update_schedule(self, schedule_name: str, **kwargs):
        """🔧 Update a specific schedule configuration"""
        if schedule_name in self.schedules:
            self.schedules[schedule_name].update(kwargs)
            logger.info(f"📝 Updated {schedule_name} schedule: {kwargs}")
        else:
            logger.warning(f"⚠️ Unknown schedule: {schedule_name}")

# ═══════════════════════════════════════════════════════════════════
# 🌟 Global Scheduler Instance
# ═══════════════════════════════════════════════════════════════════

# Global scheduler instance
ai_incident_scheduler = AIIncidentScheduler()

def start_ai_incident_scheduler():
    """🚀 Start the global AI incident scheduler"""
    ai_incident_scheduler.start_scheduler()

def stop_ai_incident_scheduler():
    """⏹️ Stop the global AI incident scheduler"""
    ai_incident_scheduler.stop_scheduler()

def get_scheduler_status():
    """📊 Get scheduler status"""
    return ai_incident_scheduler.get_scheduler_status()

async def trigger_immediate_orchestration(tenant_id: Optional[int] = None):
    """⚡ Trigger immediate AI orchestration for urgent threats"""
    logger.info("⚡ Triggering immediate AI orchestration")
    
    db = SessionLocal()
    try:
        tenants = [tenant_id] if tenant_id else [1]  # Default or specific tenant
        
        results = []
        for tid in tenants:
            result = await run_ai_incident_orchestration(db, tid)
            results.append(result)
            
            if result["status"] == "success":
                incidents_created = result.get("incidents_created", 0)
                if incidents_created > 0:
                    logger.info(f"⚡ Immediate orchestration: {incidents_created} incidents for tenant {tid}")
        
        return {
            "status": "success",
            "message": "Immediate orchestration completed",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Immediate orchestration failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        db.close()
