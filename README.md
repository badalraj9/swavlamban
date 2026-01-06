# SWARM-01 Distributed Coordination System
### Swavlamban 2025 - Challenge 1 Submission

## 🚀 Overview

SWARM-01 is a resilient, fully distributed swarm coordination system designed for the Indian Navy's "Swavlamban 2025" challenge. It implements a self-healing, leader-following swarm capable of real-time task allocation under severe adversarial conditions (packet loss, jamming, and node failures).

## 🛡️ Key Differentiators: Naval Doctrine Alignment

Unlike typical distributed systems that optimize for throughput, SWARM-01 is optimized for **Survivability and Mission Continuity**, aligning with naval operational philosophy:

1.  **Mission Continuity Mode**: Prioritizes stability over optimality. During command instability ("election storms"), the swarm freezes task assignments to prevent thrashing and maintains formation.
2.  **Degraded Operations**: Explicitly detects and logs degraded network states, adopting a conservative, low-bandwidth posture to maintain silence.
3.  **Advisory Leadership**: Units treat leadership commands as advisory during degraded states, verifying safety constraints locally before execution.
4.  **Lightweight Hardening**: Implements Identity Binding (UUID + Monotonic Term) to prevent spoofing and replay attacks without heavy cryptographic overhead.

## 🏗️ Architecture

-   **Backend (`src/`)**: Pure Python implementation of Bully Algorithm and CBAA. Dependency-free core.
-   **Frontend (`frontend/`)**: HTML5/JS "Command Interface" for real-time visualization.
-   **Communication**: Asynchronous Event-Driven Loop (10Hz guaranteed).

## 📂 Documentation

-   **[DESIGN_NOTES.md](DESIGN_NOTES.md)**: Detailed architectural decisions, security hardening strategy, and operational doctrine.
-   **[HELL_TEST_REPORT_FINAL.md](HELL_TEST_REPORT_FINAL.md)**: Verified results from the adversarial "Hell-Test" suite.
-   **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)**: Narrative script for the submission demonstration.

## 📊 Performance Metrics (Verified)

| Metric | Result | Limit/Goal |
| :--- | :--- | :--- |
| **Leader Election** | **< 4.0s** | < 10.0s |
| **Task Stability** | **> 99%** | > 95% |
| **Real-Time Loop** | **< 16ms** | < 100ms (10Hz) |
| **Packet Loss** | **Survives 50%** | > 20% |
| **Security** | **Spoofing Blocked** | N/A |

## 🛠️ Usage

### Prerequisites
-   Python 3.10+
-   `pip install -r requirements.txt`

### 1. Running the Core System (Backend)
To verify the system against adversarial scenarios (Cascading Failure, Partition, Sabotage):

```bash
export PYTHONPATH=$PYTHONPATH:.
python3 tests/hell_runner.py
```

This generates a `hell_test.log` file containing the operational history.

### 2. Running the Visualization (Frontend)
To open the "SWARM COMMAND INTERFACE" dashboard:

```bash
python3 frontend/serve.py
```

Then open your browser to: **http://localhost:8000**

*Note: The frontend is a read-only visualization layer. It reads the log file produced by the backend and does not affect the swarm's operation.*

## 📜 License
Unclassified / Open Source for Swavlamban 2025.
