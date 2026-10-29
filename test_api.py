# test_api.py
import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1/alarms/ingest"

# Simulate a live batch of raw monitoring alarms coming from an external source
payload = [
    {
        "device_id": "CORE-RTR-01",
        "severity": "CRITICAL",
        "event_description": "BGP Session Reset / Interface Line Protocol Down"
    },
    {
        "device_id": "DIST-SW-01",
        "severity": "MAJOR",
        "event_description": "OSPF Neighbor State Down via upstream gateway"
    }
]

print(f"Sending live webhook request to {API_URL}...")
response = requests.post(API_URL, json=payload)

print(f"Response Status Code: {response.status_code}")
print("Response Body:")
print(json.dumps(response.json(), indent=2))