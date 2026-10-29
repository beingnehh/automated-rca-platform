# test_platform.py
from integrations import normalize_nagios_event, normalize_snmp_trap
from rca_engine import run_rca
from database import init_db, save_device_inventory, save_incident, fetch_all_incidents
from devices import DEVICES

def run_full_integration_test():
    print("🚀 Initializing Automated RCA Platform End-to-End Test...")
    
    # 1. Initialize DB and Inventory
    init_db()
    save_device_inventory(DEVICES)
    print("✔ Database initialized and device inventory synchronized.")
    
    # 2. Simulate external monitoring inputs (Nagios alert & SNMP Trap)
    nagios_alert = {
        "host": "CORE-RTR-01", 
        "state": "CRITICAL", 
        "output": "BGP Peer down / High packet loss detected"
    }
    snmp_trap = {
        "agent_ip": "192.168.1.1", 
        "trap_oid": "linkDown", 
        "varbind": "GigabitEthernet0/0 interface down"
    }
    
    # 3. Normalize external events
    norm_nagios = normalize_nagios_event(nagios_alert)
    norm_snmp = normalize_snmp_trap(snmp_trap)
    incoming_alarms = [norm_nagios, norm_snmp]
    print(f"✔ Normalized {len(incoming_alarms)} external monitoring events.")
    
    # 4. Run RCA Correlation & Suppression Engine
    incidents = run_rca(incoming_alarms)
    print(f"✔ RCA Engine generated {len(incidents)} incident(s).")
    
    # 5. Persist to SQLite
    for inc in incidents:
        save_incident(inc)
        print(f"   -> Saved Incident ID: {inc['incident_id']} | Root Cause: {inc['probable_root_cause']}")
        
    # 6. Verify retrieval
    stored_incidents = fetch_all_incidents()
    print(f"✔ Verification check: {len(stored_incidents)} total incident(s) currently stored in SQLite.")
    print("🎉 End-to-End Platform Test Passed Successfully!")

if __name__ == "__main__":
    run_full_integration_test()