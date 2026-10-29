# integrations.py
from datetime import datetime

def normalize_nagios_event(nagios_alert):
    """
    Step 54: Normalizes a raw Nagios monitoring event into the platform's standard alarm format.
    Expected Nagios input: { "host": "CORE-RTR-01", "state": "CRITICAL", "output": "BGP Peer down", "timestamp": "..." }
    """
    severity_mapping = {
        "OK": "INFO",
        "WARNING": "MINOR",
        "CRITICAL": "CRITICAL",
        "UNKNOWN": "MAJOR"
    }
    
    normalized = {
        "device_id": nagios_alert.get("host", "UNKNOWN-DEVICE"),
        "timestamp": nagios_alert.get("timestamp", datetime.now().isoformat()),
        "severity": severity_mapping.get(nagios_alert.get("state", "CRITICAL"), "CRITICAL"),
        "event_description": f"[Nagios] {nagios_alert.get('output', 'Service check failed')}",
        "status": "active" if nagios_alert.get("state") != "OK" else "resolved"
    }
    return normalized

def normalize_snmp_trap(snmp_trap):
    """
    Step 54: Normalizes a raw SNMP Trap (e.g., from snmptrapd / SNMPTT) into the platform's standard alarm format.
    Expected SNMP input: { "agent_ip": "192.168.1.1", "trap_oid": "linkDown", "varbind": "Interface 0/1 down", "timestamp": "..." }
    """
    # Map device IP back to device ID based on inventory if needed
    ip_to_device = {
        "192.168.1.1": "CORE-RTR-01",
        "192.168.2.1": "DIST-SW-01",
        "192.168.3.1": "ACCESS-SW-01",
        "192.168.3.10": "SRV-APP-01",
        "192.168.3.20": "SRV-DB-01"
    }
    
    agent_ip = snmp_trap.get("agent_ip", "127.0.0.1")
    device_id = ip_to_device.get(agent_ip, agent_ip)
    
    severity = "CRITICAL" if "down" in snmp_trap.get("trap_oid", "").lower() else "MAJOR"
    
    normalized = {
        "device_id": device_id,
        "timestamp": snmp_trap.get("timestamp", datetime.now().isoformat()),
        "severity": severity,
        "event_description": f"[SNMP Trap] {snmp_trap.get('trap_oid')}: {snmp_trap.get('varbind', 'Trap received')}",
        "status": "active"
    }
    return normalized

if __name__ == "__main__":
    # Test normalization independently (Step 57)
    sample_nagios = {"host": "CORE-RTR-01", "state": "CRITICAL", "output": "PING CRITICAL - Packet loss = 100%"}
    sample_snmp = {"agent_ip": "192.168.1.1", "trap_oid": "linkDown", "varbind": "GigabitEthernet0/1 changed state to down"}
    
    print("Normalized Nagios:", normalize_nagios_event(sample_nagios))
    print("Normalized SNMP:", normalize_snmp_trap(sample_snmp))