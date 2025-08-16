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
Connector Scheduler - Automatically runs the Universal Data Connector pipeline
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import os

from .manager import ConnectorManager
from .config import get_connector_config

logger = logging.getLogger(__name__)


class ConnectorScheduler:
    """
    Scheduler for automatic threat collection and analysis
    """
    
    def __init__(self):
        self.running = False
        self.manager: ConnectorManager = None
        self.task: asyncio.Task = None
        self.last_run: datetime = None
        
        # Configuration
        self.poll_interval = int(os.getenv('CONNECTOR_POLL_INTERVAL', '300'))  # 5 minutes default
        self.enabled = os.getenv('CONNECTOR_SCHEDULER_ENABLED', 'true').lower() == 'true'
        self.tenant_id = int(os.getenv('DEFAULT_TENANT_ID', '1'))
    
    def start(self):
        """Start the scheduler"""
        if not self.enabled:
            logger.info("🔌 Connector scheduler disabled")
            return
            
        if self.running:
            logger.warning("Connector scheduler already running")
            return
        
        try:
            # Initialize connector manager
            config = get_connector_config()
            self.manager = ConnectorManager(config)
            
            # Start the scheduler task
            self.task = asyncio.create_task(self._scheduler_loop())
            self.running = True
            
            logger.info(f"🔌 Connector scheduler started (interval: {self.poll_interval}s)")
            
        except Exception as e:
            logger.error(f"Failed to start connector scheduler: {e}")
            self.running = False
    
    def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        self.running = False
        
        if self.task and not self.task.done():
            self.task.cancel()
        
        logger.info("🔌 Connector scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info(f"🔄 Starting connector scheduler loop")
        
        while self.running:
            try:
                # Run the pipeline
                await self._run_pipeline()
                
                # Wait for next interval
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                logger.info("Connector scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(60)
    
    async def _run_pipeline(self):
        """Run the connector pipeline"""
        try:
            start_time = datetime.utcnow()
            
            # Calculate since time (last run or default lookback)
            if self.last_run:
                since = self.last_run
            else:
                since = start_time - timedelta(hours=1)  # Default 1 hour lookback
            
            logger.info(f"🔄 Running connector pipeline (since: {since.isoformat()})")
            
            # Run pipeline in thread pool to avoid blocking
            def run_sync_pipeline():
                return self.manager.run_full_pipeline(since=since, tenant_id=self.tenant_id)
            
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_sync_pipeline)
            
            # Update last run time
            self.last_run = start_time
            
            # Log results
            if result['status'] == 'success':
                logger.info(
                    f"✅ Pipeline completed: "
                    f"{result['threats_collected']} threats, "
                    f"{result['incidents_created']} incidents, "
                    f"{result['duration']:.2f}s"
                )
            else:
                logger.error(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"Failed to run pipeline: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'enabled': self.enabled,
            'running': self.running,
            'poll_interval': self.poll_interval,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': (self.last_run + timedelta(seconds=self.poll_interval)).isoformat() 
                       if self.last_run else None,
            'tenant_id': self.tenant_id,
            'manager_initialized': self.manager is not None
        }


# Global scheduler instance
_scheduler: ConnectorScheduler = None


def get_scheduler() -> ConnectorScheduler:
    """Get or create global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = ConnectorScheduler()
    return _scheduler


def start_connector_scheduler():
    """Start the global connector scheduler"""
    scheduler = get_scheduler()
    scheduler.start()


def stop_connector_scheduler():
    """Stop the global connector scheduler"""
    scheduler = get_scheduler()
    scheduler.stop()


def get_scheduler_status() -> Dict[str, Any]:
    """Get global scheduler status"""
    scheduler = get_scheduler()
    return scheduler.get_status()
