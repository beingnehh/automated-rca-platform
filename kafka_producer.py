# kafka_producer.py
import json
from datetime import datetime
from alarm_generator import generate_scenario

# If running with real Kafka client (requires kafka-python package):
# from kafka import KafkaProducer
# producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))

def publish_scenario_to_kafka(scenario_type="router_failure"):
    """
    Publishes generated alarms to the 'network-alarms' Kafka topic.
    """
    alarms = generate_scenario(scenario_type)
    print(f"[{datetime.now().isoformat()}] Publishing {len(alarms)} alarms for scenario '{scenario_type}' to Kafka topic 'network-alarms'...")
    
    for alarm in alarms:
        # Simulated Kafka publish (or uncomment actual Kafka producer send below)
        # producer.send('network-alarms', value=alarm)
        print(f" -> Sent alarm for device: {alarm['device_id']} | Severity: {alarm['severity']}")
        
    # producer.flush()
    return alarms

if __name__ == "__main__":
    publish_scenario_to_kafka("router_failure")