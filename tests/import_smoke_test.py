import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    env.pop("DASHSCOPE_API_KEY", None)
    env.pop("DEEPSEEK_API_KEY", None)
    env["SIMULATION_SMOKE"] = "1"
    env["SIMULATION_MAX_TURNS"] = "1"
    env["SIMULATION_CONCURRENCY"] = "1"
    env["SILENT_CONSOLE"] = "1"

    proc = subprocess.run(
        [sys.executable, str(root / "src" / "simulator.py")],
        cwd=str(root),
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stdout + "\n" + proc.stderr)
    print("import_smoke_test passed")


if __name__ == "__main__":
    main()

