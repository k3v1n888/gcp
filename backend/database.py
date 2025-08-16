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

# In /backend/database.py

from .models import SessionLocal

# This is the dependency function your other files are looking for
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
