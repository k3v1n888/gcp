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
Migration script to fix NULL timestamps in existing data
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_null_timestamps():
    """Fix NULL timestamps in existing threat_logs"""
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/cyberdb")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check how many records have NULL timestamps
        result = db.execute(text("SELECT COUNT(*) FROM threat_logs WHERE timestamp IS NULL")).scalar()
        logger.info(f"Found {result} records with NULL timestamps")
        
        if result > 0:
            # Update NULL timestamps to current time
            current_time = datetime.utcnow()
            update_result = db.execute(
                text("UPDATE threat_logs SET timestamp = :current_time WHERE timestamp IS NULL"),
                {"current_time": current_time}
            )
            db.commit()
            logger.info(f"Updated {update_result.rowcount} records with current timestamp")
        
        # Verify the fix
        remaining_nulls = db.execute(text("SELECT COUNT(*) FROM threat_logs WHERE timestamp IS NULL")).scalar()
        logger.info(f"Remaining NULL timestamps: {remaining_nulls}")
        
    except Exception as e:
        logger.error(f"Error fixing timestamps: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_null_timestamps()