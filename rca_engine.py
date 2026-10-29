# rca_engine.py
from datetime import datetime
from devices import DEVICES, get_downstream_devices

def validate_and_normalize_alarm(alarm):
    """Step 15: Validate and normalize incoming alarms."""
    required_fields = ["device_id", "timestamp", "severity", "event_description"]
    for field in required_fields:
        if field not in alarm:
            raise ValueError(f"Missing required alarm field: {field}")
    
    # Normalize values
    normalized = {
        "device_id": str(alarm["device_id"]).strip(),
        "timestamp": alarm["timestamp"],
        "severity": str(alarm["severity"]).upper().strip(),
        "event_description": str(alarm["event_description"]).strip(),
        "status": str(alarm.get("status", "active")).lower().strip()
    }
    return normalized

def run_rca(raw_alarms):
    """
    Core RCA Engine workflow:
    - Normalizes alarms
    - Identifies critical root causes based on topology and timestamps
    - Groups related alarms into incidents
    - Suppresses downstream secondary alarms
    """
    normalized_alarms = [validate_and_normalize_alarm(a) for a in raw_alarms]
    
    # Sort alarms chronologically
    sorted_alarms = sorted(normalized_alarms, key=lambda x: x["timestamp"])
    
    active_alarms = [a for a in sorted_alarms if a["status"] == "active"]
    resolved_alarms = [a for a in sorted_alarms if a["status"] == "resolved"]
    
    incidents = []
    suppressed_alarm_ids = set()

    # Step 16 & 20: Identify critical failures / root causes
    # Find devices that have critical/major alarms and have no parent failing, or are the earliest critical failure
    critical_devices = [a["device_id"] for a in active_alarms if a["severity"] in ["CRITICAL", "MAJOR"]]
    
    # Determine primary root cause: Prefer devices with no parents in the active alarm list, or the very first critical alarm
    root_cause_candidates = []
    for dev_id in critical_devices:
        parent = DEVICES.get(dev_id, {}).get("parent")
        # If parent is not actively raising an alarm, this is a strong root cause candidate
        if not parent or parent not in critical_devices:
            root_cause_candidates.append(dev_id)

    # If we found root cause candidates, pick the first one as primary incident
    if root_cause_candidates:
        primary_root = root_cause_candidates[0]
        downstream = get_downstream_devices(primary_root)
        
        related_alarms = []
        suppressed_alarms = []

        for alarm in active_alarms:
            d_id = alarm["device_id"]
            if d_id == primary_root:
                related_alarms.append(alarm)
            elif d_id in downstream:
                # Step 22: Mark correlated secondary alarms as suppressed
                alarm_copy = alarm.copy()
                alarm_copy["suppression_reason"] = f"Downstream effect of parent failure: {primary_root}"
                suppressed_alarms.append(alarm_copy)
                suppressed_alarm_ids.add((d_id, alarm["timestamp"]))
                related_alarms.append(alarm_copy)
            else:
                # Unrelated or separate failure
                related_alarms.append(alarm)

        incident = {
            "incident_id": f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "probable_root_cause": primary_root,
            "root_cause_name": DEVICES.get(primary_root, {}).get("name", primary_root),
            "severity": "CRITICAL",
            "status": "ACTIVE",
            "alarms": related_alarms,
            "explanation": f"Root cause identified at {primary_root} ({DEVICES.get(primary_root, {}).get('name', '')}). {len(suppressed_alarms)} downstream alarm(s) suppressed due to dependency mapping."
        }
        incidents.append(incident)

    elif resolved_alarms:
        # Handle recovery scenario
        incidents.append({
            "incident_id": f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "probable_root_cause": "SYSTEM RECOVERY",
            "root_cause_name": "All Systems Operational",
            "severity": "INFO",
            "status": "RESOLVED",
            "alarms": resolved_alarms,
            "explanation": "Network recovery detected. All systems reported operational status."
        })

    return incidents