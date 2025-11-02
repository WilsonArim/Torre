from __future__ import annotations
from typing import Dict, Any
from .vanguard_brief import validate_brief

def propose_to_canon(brief: Dict[str, Any], approver: str, approve: bool=False) -> Dict[str, Any]:
    """
    Porta de promoção ao CANON. Só aprova se gates ok e 'approve=True'.
    """
    v = validate_brief(brief)
    status = "pending"
    if not v["ok"]:
        status = "rejected"
    elif approve:
        status = "approved"
    return {
        "status": status,
        "validated": v,
        "approved_by": approver if status == "approved" else None,
        "record": {
            "kind": "VANGUARD_BRIEF",
            "hash": hash(str(brief)) & 0xffffffff,
        } if status != "rejected" else None,
    }
