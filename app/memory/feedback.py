from collections import defaultdict
from app.memory.store import decision_history

# product_id → feedback list
feedback_db = defaultdict(list)


def save_feedback(product_id: str, payload: dict):
    """
    Safely attach feedback to history
    """

    for entry in reversed(decision_history):

        # skip invalid history items
        if not isinstance(entry, dict):
            continue

        actions = entry.get("final_actions", [])

        for action in actions:
            if isinstance(action, dict) and action.get("product_id") == product_id:
                entry.setdefault("feedback", []).append(payload)
                break

    feedback_db[product_id].append(payload)

    return {"status": "stored"}


def get_feedback(product_id: str):
    return feedback_db.get(product_id, [])
