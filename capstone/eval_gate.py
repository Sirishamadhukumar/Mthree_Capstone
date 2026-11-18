"""Command-line evaluation gate for capstone reports."""

import json
import sys
from pathlib import Path


def main(argv=None):
    # Read arguments supplied by the user or CI pipeline.
    args = list(sys.argv[1:] if argv is None else argv)

    # Show usage information when requested.
    usage = (
        "Usage: python eval_gate.py FILE.json "
        "[--min metric=value] [--max metric=value]"
    )

    if not args:
        print(usage)
        return 2

    if args[0] in ("-h", "--help"):
        print(usage)
        return 0

    # Load the evaluation report.
    report_path = Path(args.pop(0))

    try:
        with report_path.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Cannot read results: {error}")
        return 2

    # Collect supported evaluation metrics.
    metrics = report.get("metrics", {})
    latency = report.get("latency_ms", {})

    if not isinstance(metrics, dict) or not isinstance(latency, dict):
        print("Invalid report: metrics and latency_ms must be objects.")
        return 2

    values = dict(metrics)
    values["latency_p50_ms"] = latency.get("p50")
    values["latency_p95_ms"] = latency.get("p95")
    values["sim_cost_usd"] = report.get("sim_cost_usd")

    # Validate the threshold arguments before evaluating them.
    thresholds = []
    index = 0

    while index < len(args):
        flag = args[index]

        if flag not in ("--min", "--max") or index + 1 >= len(args):
            print(f"Invalid threshold arguments. {usage}")
            return 2

        expression = args[index + 1]

        if "=" not in expression:
            print(f"Invalid threshold: {expression}")
            return 2

        metric_name, threshold_text = expression.split("=", 1)

        if not metric_name:
            print(f"Invalid threshold: {expression}")
            return 2

        try:
            threshold = float(threshold_text)
        except ValueError:
            print(f"Invalid numeric threshold: {expression}")
            return 2

        thresholds.append((flag, metric_name, threshold))
        index += 2

    # Check every requested threshold.
    failed = False

    for flag, metric_name, threshold in thresholds:
        actual_value = values.get(metric_name)

        try:
            actual = float(actual_value)
        except (TypeError, ValueError):
            print(f"FAIL {metric_name}: metric missing or non-numeric")
            failed = True
            continue

        if flag == "--min":
            passed = actual >= threshold
            operator = ">="
        else:
            passed = actual <= threshold
            operator = "<="

        result = "PASS" if passed else "FAIL"

        print(
            f"{result} {metric_name}: "
            f"{actual:.4f} {operator} {threshold:.4f}"
        )

        if not passed:
            failed = True

    # Exit 1 if any threshold fails; otherwise exit 0.
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())