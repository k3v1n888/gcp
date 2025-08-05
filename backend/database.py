# In /backend/database.py

from .models import SessionLocal

# This is the dependency function your other files are looking for
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
