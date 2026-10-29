# devices.py

# Dictionary of network devices with their attributes and parent dependencies
DEVICES = {
    "CORE-RTR-01": {
        "name": "Core Router 01",
        "type": "router",
        "ip": "192.168.1.1",
        "parent": None
    },
    "DIST-SW-01": {
        "name": "Distribution Switch 01",
        "type": "switch",
        "ip": "192.168.2.1",
        "parent": "CORE-RTR-01"
    },
    "ACCESS-SW-01": {
        "name": "Access Switch 01",
        "type": "switch",
        "ip": "192.168.3.1",
        "parent": "DIST-SW-01"
    },
    "SRV-APP-01": {
        "name": "Application Server 01",
        "type": "server",
        "ip": "192.168.3.10",
        "parent": "ACCESS-SW-01"
    },
    "SRV-DB-01": {
        "name": "Database Server 01",
        "type": "server",
        "ip": "192.168.3.20",
        "parent": "ACCESS-SW-01"
    }
}

def get_downstream_devices(device_id):
    """Returns a list of all devices that depend on the given device ID."""
    downstream = []
    for dev_id, info in DEVICES.items():
        if info["parent"] == device_id:
            downstream.append(dev_id)
            downstream.extend(get_downstream_devices(dev_id))
    return downstream