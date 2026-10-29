# api_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from integrations import normalize_nagios_event, normalize_snmp_trap
from rca_engine import run_rca
from database import init_db, save_incident, save_device_inventory
from devices import DEVICES

app = FastAPI(
    title="Automated RCA Platform API",
    description="Enterprise backend API for real-time alarm ingestion, normalization, and RCA correlation.",
    version="1.0"
)

# Initialize Database and Device Inventory on startup
init_db()
save_device_inventory(DEVICES)

class RawAlarm(BaseModel):
    device_id: str
    timestamp: Optional[str] = None
    severity: str
    event_description: str
    status: Optional[str] = "active"

@app.get("/")
def health_check():
    return {"status": "ONLINE", "engine": "RCA Correlation Pipeline Active", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/alarms/ingest")
def ingest_alarms(alarms: List[RawAlarm]):
    """
    Ingests a batch of raw alarms, runs the RCA correlation engine, 
    suppresses downstream noise, and stores incidents in SQLite.
    """
    try:
        raw_data = [a.dict() for a in alarms]
        for item in raw_data:
            if not item["timestamp"]:
                item["timestamp"] = datetime.now().isoformat()
        
        # Run core backend RCA engine
        incidents = run_rca(raw_data)
        
        # Persist results
        for inc in incidents:
            save_incident(inc)
            
        return {
            "status": "success", 
            "processed_alarms_count": len(raw_data), 
            "generated_incidents_count": len(incidents),
            "incidents": incidents
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/nagios")
def ingest_nagios(alert: Dict[str, Any]):
    """Ingests, normalizes, and runs RCA on an incoming Nagios event."""
    try:
        normalized = normalize_nagios_event(alert)
        incidents = run_rca([normalized])
        for inc in incidents:
            save_incident(inc)
        return {"status": "success", "source": "Nagios", "normalized_alarm": normalized, "incidents": incidents}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/snmp")
def ingest_snmp(trap: Dict[str, Any]):
    """Ingests, normalizes, and runs RCA on an incoming SNMP trap."""
    try:
        normalized = normalize_snmp_trap(trap)
        incidents = run_rca([normalized])
        for inc in incidents:
            save_incident(inc)
        return {"status": "success", "source": "SNMP Trap", "normalized_alarm": normalized, "incidents": incidents}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))