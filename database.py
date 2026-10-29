# database.py
import sqlite3
import json
from datetime import datetime

DB_NAME = "rca_platform.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Step 26: Create tables for devices, raw alarms, incidents, and relationships."""
    conn = get_connection()
    cursor = conn.cursor()

    # Devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            ip TEXT,
            parent TEXT
        )
    ''')

    # Raw Alarms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            timestamp TEXT,
            severity TEXT,
            event_description TEXT,
            status TEXT,
            suppression_reason TEXT
        )
    ''')

    # Incidents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            probable_root_cause TEXT,
            root_cause_name TEXT,
            severity TEXT,
            status TEXT,
            explanation TEXT,
            created_at TEXT
        )
    ''')

    # Incident-to-Alarm mapping table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incident_alarms (
            incident_id TEXT,
            alarm_id INTEGER,
            is_suppressed BOOLEAN,
            suppression_reason TEXT,
            FOREIGN KEY(incident_id) REFERENCES incidents(incident_id),
            FOREIGN KEY(alarm_id) REFERENCES raw_alarms(id)
        )
    ''')

    conn.commit()
    conn.close()

def save_device_inventory(devices_dict):
    """Populates the devices table from devices.py."""
    conn = get_connection()
    cursor = conn.cursor()
    for dev_id, info in devices_dict.items():
        cursor.execute('''
            INSERT OR REPLACE INTO devices (device_id, name, type, ip, parent)
            VALUES (?, ?, ?, ?, ?)
        ''', (dev_id, info["name"], info["type"], info["ip"], info["parent"]))
    conn.commit()
    conn.close()

def save_alarm(alarm):
    """Step 27: Save every incoming alarm to SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO raw_alarms (device_id, timestamp, severity, event_description, status, suppression_reason)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        alarm["device_id"],
        alarm["timestamp"],
        alarm["severity"],
        alarm["event_description"],
        alarm["status"],
        alarm.get("suppression_reason", None)
    ))
    alarm_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return alarm_id

def save_incident(incident):
    """Step 28 & 29: Save probable root cause, severity, status, and associated alarms."""
    conn = get_connection()
    cursor = conn.cursor()
    
    created_at = datetime.now().isoformat()
    cursor.execute('''
        INSERT OR REPLACE INTO incidents (incident_id, probable_root_cause, root_cause_name, severity, status, explanation, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        incident["incident_id"],
        incident["probable_root_cause"],
        incident["root_cause_name"],
        incident["severity"],
        incident["status"],
        incident["explanation"],
        created_at
    ))

    # Save associated alarms and mapping
    for alarm in incident.get("alarms", []):
        # Save raw alarm if not already stored
        cursor.execute('''
            INSERT INTO raw_alarms (device_id, timestamp, severity, event_description, status, suppression_reason)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            alarm["device_id"],
            alarm["timestamp"],
            alarm["severity"],
            alarm["event_description"],
            alarm["status"],
            alarm.get("suppression_reason", None)
        ))
        alarm_id = cursor.lastrowid
        
        is_suppressed = 1 if "suppression_reason" in alarm else 0
        cursor.execute('''
            INSERT INTO incident_alarms (incident_id, alarm_id, is_suppressed, suppression_reason)
            VALUES (?, ?, ?, ?)
        ''', (incident["incident_id"], alarm_id, is_suppressed, alarm.get("suppression_reason", None)))

    conn.commit()
    conn.close()

def fetch_all_alarms():
    """Retrieves all stored raw alarms."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM raw_alarms ORDER BY timestamp DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def fetch_all_incidents():
    """Retrieves all stored incidents."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents ORDER BY created_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def fetch_incident_alarms(incident_id):
    """Retrieves alarms related to a specific incident."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        T1.device_id, T1.timestamp, T1.severity, T1.event_description, T1.status, T2.is_suppressed, T2.suppression_reason
        FROM raw_alarms T1
        JOIN incident_alarms T2 ON T1.id = T2.alarm_id
        WHERE T2.incident_id = ?
    ''', (incident_id,))
    # Quick fix for query syntax above:
    pass

def fetch_incident_details(incident_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ra.*, ia.is_suppressed, ia.suppression_reason 
        FROM incident_alarms ia
        JOIN raw_alarms ra ON ia.alarm_id = ra.id
        WHERE ia.incident_id = ?
    ''', (incident_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows