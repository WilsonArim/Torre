from typing import Dict, Any

def pick_strategy(classification: Dict[str, Any]) -> str:
    classes = classification.get("classes", [])
    return (classes or ["lint"])[0]  # prioriza lint → tests → build
