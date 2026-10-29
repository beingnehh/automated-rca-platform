# 🛡️ Enterprise Automated Root Cause Analysis (RCA) & NOC Platform

An enterprise-grade, real-time Network Operations Center (NOC) and fault correlation platform designed to eliminate alert fatigue, map infrastructure topology, ingest multi-source telemetry, and automatically isolate root causes while suppressing downstream noise.

---

## 🏗️ System Architecture & Tech Stack

- **Frontend & Dashboard:** Python, Streamlit (Custom Dark-Mode NOC UI, Plotly Analytics)
- **Core Engine & Logic:** Python (Topology dependency mapping, deterministic RCA, alarm suppression)
- **Messaging & Streaming:** Apache Kafka (`network-alarms` event bus producer/consumer)
- **Persistence Layer:** SQLite (Relational storage for devices, raw event streams, incidents, and mappings)
- **Monitoring Integrations:** Nagios monitoring alerts & SNMP Trap normalization adapters

---

## 📂 Project Structure

```text
automated-rca-platform/
│
├── devices.py            # Infrastructure topology & parent-child mapping
├── alarm_generator.py    # Repeatable failure scenario simulation engine
├── rca_engine.py         # Alarm normalization, RCA correlation, and noise suppression
├── database.py           # SQLite persistence schema and CRUD operations
├── kafka_producer.py     # Real-time event streaming producer
├── kafka_consumer.py     # Stream consumer feeding RCA engine and database
├── integrations.py       # Nagios and SNMP Trap normalization adapters
├── test_platform.py      # End-to-end automated integration testing
└── app.py                # Streamlit NOC Dashboard & Command Hub