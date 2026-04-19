from __future__ import annotations

import argparse
import csv
import math
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List


def _parse_percent(s: str) -> float:
    t = (s or "").strip()
    if not t:
        return 0.0
    if t.endswith("%"):
        return float(t[:-1]) / 100.0
    return float(t)


def _read_summary_metrics(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _aggregate_metrics(run_rows: List[List[Dict[str, str]]]) -> List[Dict[str, str]]:
    metrics = [
        "Identification Accuracy",
        "Cognitive Correction Rate",
        "Avg Turns",
        "Refusal Success Rate",
        "Guardrail Interception Rate",
        "Answer Leakage Rate",
        "Transition Success Rate",
        "Abnormal Termination Rate",
    ]

    by_version: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    for rows in run_rows:
        for r in rows:
            v = r["Version"]
            for k in metrics:
                if k == "Avg Turns":
                    by_version[v][k].append(float(r[k]))
                else:
                    by_version[v][k].append(_parse_percent(r[k]))

    out: List[Dict[str, str]] = []
    n = len(run_rows)

    for v in sorted(by_version.keys()):
        row: Dict[str, str] = {"Version": v, "N": str(n)}
        for k in metrics:
            xs = by_version[v][k]
            m = mean(xs) if xs else 0.0
            sd = stdev(xs) if len(xs) >= 2 else 0.0
            ci95 = 1.96 * sd / math.sqrt(len(xs)) if len(xs) >= 2 else 0.0
            if k == "Avg Turns":
                row[f"{k} Mean"] = f"{m:.2f}"
                row[f"{k} Std"] = f"{sd:.2f}"
                row[f"{k} CI95"] = f"{ci95:.2f}"
            else:
                row[f"{k} Mean"] = f"{m:.2%}"
                row[f"{k} Std"] = f"{sd:.2%}"
                row[f"{k} CI95"] = f"{ci95:.2%}"
        out.append(row)

    return out


def _write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_md(path: Path, rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    headers = list(rows[0].keys())
    lines = []
    lines.append("# Experiment Suite Summary")
    lines.append("")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(h, "")) for h in headers) + " |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _run_pipeline(
    log_dir: Path, results_dir: Path, pipeline_log: Path, env: Dict[str, str], include_judge: bool
) -> None:
    cmds = [
        [sys.executable, "src/simulator.py"],
        [sys.executable, "src/evaluator.py"],
    ]
    if include_judge:
        cmds.append([sys.executable, "src/llm_judge.py"])

    env = {**os.environ, **env}
    env["LOG_DIR"] = str(log_dir)
    env["RESULTS_DIR"] = str(results_dir)

    log_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    with pipeline_log.open("w", encoding="utf-8") as f:
        for cmd in cmds:
            subprocess.run(
                cmd,
                cwd=str(Path(__file__).resolve().parent.parent),
                env=env,
                stdout=f,
                stderr=subprocess.STDOUT,
                check=True,
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=int(os.environ.get("EXP_RUNS", "5")))
    parser.add_argument("--out-dir", type=str, default=os.environ.get("EXP_OUT_DIR", "experiments"))
    parser.add_argument("--seed", type=int, default=int(os.environ.get("EXP_SEED", "0")))
    parser.add_argument("--no-judge", action="store_true")
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    root = Path(args.out_dir).resolve() / f"suite_{ts}"
    root.mkdir(parents=True, exist_ok=True)

    run_rows: List[List[Dict[str, str]]] = []
    include_judge = not args.no_judge

    for i in range(args.runs):
        run_id = f"run_{i + 1:02d}"
        run_dir = root / run_id
        log_dir = run_dir / "logs"
        results_dir = run_dir / "results"
        pipeline_log = run_dir / "pipeline.log"

        env = {
            "SIMULATION_CLEAN_LOGS": "1",
            "SILENT_CONSOLE": "1",
        }
        if args.seed:
            env["SIMULATION_SEED"] = str(args.seed + i)

        _run_pipeline(log_dir, results_dir, pipeline_log, env=env, include_judge=include_judge)

        summary_path = results_dir / "summary_metrics.csv"
        run_rows.append(_read_summary_metrics(summary_path))

    agg = _aggregate_metrics(run_rows)
    _write_csv(root / "aggregate_summary.csv", agg)
    _write_md(root / "aggregate_summary.md", agg)
    print(str(root))


if __name__ == "__main__":
    main()
