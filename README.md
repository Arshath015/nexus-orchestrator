# Nexus Meta-Agent Orchestrator

AI-Driven Decision Fusion System for Multi-Bot Coordination

---

## Overview

This project implements a lightweight orchestration layer that simulates how a meta-agent evaluates and merges actions proposed by multiple intelligent agents.

It demonstrates structured reasoning, conflict detection, memory persistence, and evaluation benchmarking using an LLM-driven pipeline.

The system is designed as a backend decision engine accessible via API endpoints.

---

## Key Capabilities

- Accepts multi-agent proposed actions
- Detects logical conflicts
- Produces structured reasoning traces
- Determines final execution actions
- Stores decision history
- Accepts user feedback
- Generates evaluation reports

Schema layer reserved for request/response validation expansion.

---

## Architecture

```bash
API Layer (FastAPI)
↓
Orchestrator Service
↓
LLM Decision Engine
↓
Memory Storage
↓
Evaluation Engine
```

---

## Project Structure

```bash
app/
├── api/
│ └── routes.py
├── services/
│ ├── orchestrator.py
│ └── llm_service.py
├── memory/
│ ├── store.py
│ └── feedback.py
├── models/
└── main.py
└── evaluate_orchestrator.py
└── poc_test_scenarios.json
```

---

## API Endpoints

### Decision

POST /orchestrator/decide

### Feedback

POST /orchestrator/feedback

### History

GET /orchestrator/history/{product_id}

### Insights

GET /orchestrator/insights

---

## Running the Project

### Create Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```


### Start Server
```bash
uvicorn app.main:app --reload
```

Access docs:
```bash
http://127.0.0.1:8000/docs
```

---

## Evaluation

Run benchmark scenarios:
```bash
python evaluate_orchestrator.py
```

Generates:

- evaluation_results.json
- evaluation_report.md

---

## Example Decision Output

```json
{
  "conflicts": [],
  "reasoning_trace": [
    "Inventory sufficient",
    "No policy violation detected"
  ],
  "final_actions": [
    {"action":"approve","product_id":"123"}
  ],
  "projected_outcome": {
    "status":"success"
  }
}
```

---

## Engineering Highlights

1. Resilient JSON extraction from LLM responses
2. Prompt-driven structured reasoning
3. Modular service abstraction
4. Stateless API interface
5. Lightweight in-memory persistence
6. Automated evaluation harness

---

## Future Extensions

1. Vector database memory
2. Agent weighting strategies
3. Streaming responses
4. Docker deployment
5. Cloud model integration
6. Observability dashboard

---

## Author

Arshath Farwyz
AI Engineer
