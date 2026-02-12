import json
import re
from app.services.llm_service import ask_llm
from collections import Counter
from app.memory.store import save_decision, decision_history
import concurrent.futures

SYSTEM_PROMPT = """
You are a commerce meta-agent orchestrator.

Analyze proposed bot actions and produce a structured decision.

Return ONLY valid JSON — no text outside JSON.

Format:

{
  "conflicts": [
    {"type": "", "description": ""}
  ],
  "reasoning_trace": [
    "step-by-step reasoning"
  ],
  "final_actions": [
    {
      "bot": "",
      "action": "",
      "product_id": "",
      "decision": "approved | modified | rejected",
      "justification": ""
    }
  ],
  "projected_outcome": {
    "revenue_impact": "",
    "inventory_effect": "",
    "risk_assessment": ""
  }
}
"""

def clean_json(text: str):
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # Extract first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return text.strip()

def run_orchestration(payload: dict):

    prompt = SYSTEM_PROMPT + "\nINPUT:\n" + json.dumps(payload)

    try:
        raw = ask_llm(prompt)

        # ---------- Clean ----------
        text = clean_json(raw)

        try:
            structured = json.loads(text)
        except Exception:
            structured = {}

        # ---------- HARD SAFETY ----------
        if not isinstance(structured, dict):
            structured = {}

        structured.setdefault("conflicts", [])
        structured.setdefault("reasoning_trace", [])
        structured.setdefault("final_actions", [])
        structured.setdefault("projected_outcome", {})

        # ---------- Normalize conflicts ----------
        if structured["conflicts"] and isinstance(structured["conflicts"][0], dict):
            structured["conflicts"] = [
                c.get("type", "unknown")
                for c in structured["conflicts"]
            ]

        # ---------- Save history ----------
        for action in structured.get("final_actions", []):
            pid = action.get("product_id")
            if pid:
                record = {
                    "conflicts": structured["conflicts"],
                    "final_actions": structured["final_actions"],
                    "projected_outcome": structured["projected_outcome"],
                }
                save_decision(pid, record)

        return structured

    # ---------- GLOBAL FAILSAFE ----------
    except Exception as e:
        return {
            "conflicts": [],
            "reasoning_trace": [],
            "final_actions": [],
            "projected_outcome": {},
            "error": str(e)
        }
    
def get_insights():
    if not decision_history:
        return {"message": "No decisions recorded yet"}

    total_decisions = len(decision_history)
    total_actions = 0

    decision_counter = Counter()
    bot_counter = Counter()
    conflict_count = 0
    negative_feedback = 0

    for entry in decision_history:

        # Skip malformed entries
        if not isinstance(entry, dict):
            continue

        # Count conflicts
        conflicts = entry.get("conflicts", [])
        if isinstance(conflicts, list) and conflicts:
            conflict_count += 1

        # Count actions
        actions = entry.get("final_actions", [])
        if isinstance(actions, list):
            total_actions += len(actions)

            for action in actions:
                if isinstance(action, dict):
                    decision = action.get("decision")
                    bot = action.get("bot")

                    if decision:
                        decision_counter[decision] += 1
                    if bot:
                        bot_counter[bot] += 1

        # Optional feedback tracking
        feedback = entry.get("feedback")
        if feedback and feedback.get("rating", 0) < 0:
            negative_feedback += 1

    return {
        "total_decisions": total_decisions,
        "total_actions": total_actions,
        "approval_rate": decision_counter["approved"] / max(total_actions,1),
        "rejection_rate": decision_counter["rejected"] / max(total_actions,1),
        "modified_rate": decision_counter["modified"] / max(total_actions,1),
        "top_bot": bot_counter.most_common(1)[0][0] if bot_counter else None,
        "conflicts_detected": conflict_count,
        "negative_feedback": negative_feedback
    }