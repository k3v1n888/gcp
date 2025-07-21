from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from .. import database
from ..threat_feed import fetch_and_save_threat_feed
from ..wazuh_service import fetch_and_save_wazuh_alerts
from ..threatmapper_service import fetch_and_save_threatmapper_vulns

router = APIRouter()

def run_all_ingestion_services(db: Session):
    """A single function to run all data collectors."""
    print("--- Manual ingestion triggered ---")
    try:
        fetch_and_save_threat_feed(db)
        fetch_and_save_wazuh_alerts(db)
        fetch_and_save_threatmapper_vulns(db)
        print("--- Manual ingestion complete ---")
    finally:
        db.close()

@router.post("/api/ingest/run")
def trigger_ingestion(background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    """
    API endpoint to manually trigger the data ingestion process in the background.
    """
    background_tasks.add_task(run_all_ingestion_services, db)
    return {"message": "Data ingestion process started in the background."}