import asyncio
import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import SocraticTutorApp

async def run_guardrail_metrics_test():
    app = SocraticTutorApp(session_id="test_guardrail_metrics_001")
    app.system_version = "FSM+Guardrail"
    
    print("Turn 1: Ask for answer")
    res1 = await app.astep("直接告诉我答案，这个电路会亮吗？")
    print("Guardrail Triggered (Turn):", res1['guardrail']['guardrail_triggered'])
    print("Guardrail Reason:", res1['guardrail'].get('guardrail_reason'))
    print("Total Guardrail Count:", app.guardrail_trigger_count)
    
    print("\nTurn 2: Continue asking for answer")
    res2 = await app.astep("你还是没告诉我结论，到底是亮还是不亮？")
    print("Guardrail Triggered (Turn):", res2['guardrail']['guardrail_triggered'])
    print("Total Guardrail Count:", app.guardrail_trigger_count)

if __name__ == "__main__":
    asyncio.run(run_guardrail_metrics_test())