# kafka_consumer.py
import json
from datetime import datetime
from rca_engine import run_rca
from database import save_incident

# If running with real Kafka client:
# from kafka import KafkaConsumer
# consumer = KafkaConsumer('network-alarms', bootstrap_servers=['localhost:9092'], value_deserializer=lambda x: json.loads(x.decode('utf-8')))

def consume_and_process_alarms(incoming_alarms):
    """
    Simulates the Kafka consumer receiving streaming alarms, 
    running the RCA engine, and persisting incidents to SQLite.
    """
    print(f"[{datetime.now().isoformat()}] Consumer received batch of {len(incoming_alarms)} alarms from Kafka stream.")
    
    # Run RCA correlation and suppression
    incidents = run_rca(incoming_alarms)
    
    # Save processed incidents and alarms to database
    for inc in incidents:
        save_incident(inc)
        print(f" ✅ Processed & Saved Incident: {inc['incident_id']} | Root Cause: {inc['probable_root_cause']}")

if __name__ == "__main__":
    from alarm_generator import generate_scenario
    sample_stream = generate_scenario("router_failure")
    consume_and_process_alarms(sample_stream)