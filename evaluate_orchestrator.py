import json
import requests
import time
from datetime import datetime
from pathlib import Path
from statistics import mean

# ======================================================
# CONFIG
# ======================================================

BASE_URL = "http://127.0.0.1:8000/orchestrator"
SCENARIO_FILE = "poc_test_scenarios.json"
RESULT_JSON = "evaluation_results.json"
REPORT_MD = "evaluation_report.md"


# ======================================================
# API CALLS
# ======================================================

def post_decide(payload):
    start = time.time()
    r = requests.post(f"{BASE_URL}/decide", json=payload)
    latency = time.time() - start
    r.raise_for_status()
    return r.json(), latency


def post_feedback(payload):
    r = requests.post(f"{BASE_URL}/feedback", json=payload)
    r.raise_for_status()
    return r.json()


def get_insights():
    r = requests.get(f"{BASE_URL}/insights")
    r.raise_for_status()
    return r.json()


# ======================================================
# SCORING LOGIC
# ======================================================

def score_conflicts(expected, detected):
    detected_set = set(detected)
    expected_set = set(expected)

    correct = expected_set.intersection(detected_set)
    missed = expected_set - detected_set
    extra = detected_set - expected_set

    return {
        "correct": list(correct),
        "missed": list(missed),
        "extra": list(extra),
        "score": len(correct) / max(len(expected_set), 1)
    }


# ======================================================
# MAIN RUNNER
# ======================================================

def run():

    scenarios = json.load(open(SCENARIO_FILE))
    if isinstance(scenarios, dict):
        scenarios = scenarios["scenarios"]

    results = []
    latencies = []

    for sc in scenarios:

        print(f"Running {sc['id']}")

        entry = {
            "scenario_id": sc["id"],
            "difficulty": sc.get("difficulty"),
            "description": sc.get("description"),
            "timestamp": datetime.utcnow().isoformat()
        }

        try:

            # ----------------------------------------
            # Decision Scenario
            # ----------------------------------------
            if "input" in sc:

                resp, latency = post_decide(sc["input"])
                latencies.append(latency)

                detected = resp.get("conflicts", [])
                expected = sc.get("expected_conflict_types", [])

                scoring = score_conflicts(expected, detected)

                entry.update({
                    "latency_sec": latency,
                    "expected_conflicts": expected,
                    "detected_conflicts": detected,
                    "scoring": scoring,
                    "final_actions": resp.get("final_actions")
                })

            # ----------------------------------------
            # Feedback Scenario
            # ----------------------------------------
            elif sc.get("type") == "feedback_scenario":

                payload = {
                    "product_id": sc["previous_decision"]["resolution_id"],
                    "reviewer": "auto_runner",
                    "comment": json.dumps(sc["actual_outcome"]),
                    "rating": -1
                }

                fb = post_feedback(payload)
                entry["feedback_result"] = fb

            entry["status"] = "success"

        except Exception as e:
            entry["status"] = "failed"
            entry["error"] = str(e)

        results.append(entry)

    # ----------------------------------------
    # Save JSON
    # ----------------------------------------
    Path(RESULT_JSON).write_text(json.dumps(results, indent=2))

    # ----------------------------------------
    # Generate Markdown Report
    # ----------------------------------------
    generate_report(results, latencies)


# ======================================================
# REPORT GENERATOR
# ======================================================

def generate_report(results, latencies):

    total = len(results)
    success = sum(r["status"] == "success" for r in results)

    avg_latency = mean(latencies) if latencies else 0

    scores = [
        r.get("scoring", {}).get("score", 0)
        for r in results
        if r.get("status") == "success"
    ]

    overall_score = mean(scores) if scores else 0

    md = f"""
# Nexus Orchestrator Evaluation Report

## Run Timestamp
{datetime.utcnow().isoformat()}

---

## Summary Metrics

| Metric | Value |
|-------|------|
| Total Scenarios | {total} |
| Successful Runs | {success} |
| Avg Latency | {avg_latency:.3f}s |
| Conflict Detection Score | {overall_score:.2f} |

---

## Scenario Breakdown
"""

    for r in results:
        md += f"""
### {r['scenario_id']}
**Difficulty:** {r.get('difficulty')}  
**Status:** {r['status']}  

Expected Conflicts: {r.get('expected_conflicts')}  
Detected Conflicts: {r.get('detected_conflicts')}  
Score: {r.get('scoring',{}).get('score')}  

Latency: {r.get('latency_sec')}

---
"""

    Path(REPORT_MD).write_text(md)
    print("\nReport saved →", REPORT_MD)


# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":
    run()
