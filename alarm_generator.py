# alarm_generator.py
from datetime import datetime, timedelta
from devices import DEVICES

def generate_alarm(device_id, severity, event_description, status="active", timestamp=None):
    """Helper to generate a single standardized alarm dictionary."""
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    return {
        "device_id": device_id,
        "timestamp": timestamp,
        "severity": severity,
        "event_description": event_description,
        "status": status
    }

def generate_scenario(scenario_type="router_failure"):
    """
    Generates repeatable failure scenarios for testing.
    Supported scenarios: 'router_failure', 'switch_failure', 'recovery'
    """
    now = datetime.now()
    alarms = []

    if scenario_type == "router_failure":
        # Core router fails, causing cascading downstream alarms
        alarms.append(generate_alarm("CORE-RTR-01", "CRITICAL", "Device unreachable / BGP session down", "active", now.isoformat()))
        alarms.append(generate_alarm("DIST-SW-01", "MAJOR", "Uplink interface down", "active", (now + timedelta(seconds=2)).isoformat()))
        alarms.append(generate_alarm("ACCESS-SW-01", "MINOR", "Link lost to distribution layer", "active", (now + timedelta(seconds=4)).isoformat()))
        alarms.append(generate_alarm("SRV-APP-01", "CRITICAL", "Ping timeout / Network unreachable", "active", (now + timedelta(seconds=6)).isoformat()))
        alarms.append(generate_alarm("SRV-DB-01", "CRITICAL", "Ping timeout / Network unreachable", "active", (now + timedelta(seconds=6)).isoformat()))

    elif scenario_type == "switch_failure":
        # Access switch fails independently
        alarms.append(generate_alarm("ACCESS-SW-01", "CRITICAL", "Switch power supply failure", "active", now.isoformat()))
        alarms.append(generate_alarm("SRV-APP-01", "CRITICAL", "Host unreachable", "active", (now + timedelta(seconds=2)).isoformat()))
        alarms.append(generate_alarm("SRV-DB-01", "CRITICAL", "Host unreachable", "active", (now + timedelta(seconds=2)).isoformat()))

    elif scenario_type == "recovery":
        # Core router and dependencies recover
        alarms.append(generate_alarm("CORE-RTR-01", "INFO", "Device recovered / BGP session established", "resolved", now.isoformat()))
        alarms.append(generate_alarm("DIST-SW-01", "INFO", "Uplink interface operational", "resolved", (now + timedelta(seconds=2)).isoformat()))

    return alarms