from pathlib import Path
import json

def test_memory_policy_exists():
    assert Path("MEMORY_POLICY.md").exists()

def test_golden_runner_imports():
    import evals.golden.run_golden as rg
    assert callable(rg.main)

def test_redteam_runner_imports():
    import evals.redteam.run_redteam as rr
    assert callable(rr.main)
