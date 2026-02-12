from collections import defaultdict

# product_id → list of decisions
decision_history = defaultdict(list)


def save_decision(product_id: str, decision: dict):
    decision_history[product_id].append(decision)


def get_history(product_id: str):
    return decision_history.get(product_id, [])
