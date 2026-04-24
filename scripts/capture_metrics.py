#!/usr/bin/env python3
"""
Generic metrics extraction from skill output.

Usage:
    python capture_metrics.py "<skill_output>"
    python capture_metrics.py --file output.txt
    python capture_metrics.py --file output.txt --config config.json

Outputs JSON with all discovered metrics.
"""

import argparse
import json
import re
import sys
from typing import Any


def extract_json_blocks(text: str) -> list[dict]:
    """Extract all JSON objects from text."""
    blocks = []
    # Match JSON objects (simple heuristic: { ... })
    pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    for match in re.finditer(pattern, text):
        try:
            obj = json.loads(match.group())
            if isinstance(obj, dict):
                blocks.append(obj)
        except json.JSONDecodeError:
            continue
    return blocks


def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    """Flatten nested dict into single level with underscore-joined keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def parse_value(s: str) -> int | float | bool | str:
    """Parse string to appropriate type."""
    s = s.strip()
    if s.upper() in ('TRUE', 'PASS', 'YES', 'OK'):
        return True
    if s.upper() in ('FALSE', 'FAIL', 'NO', 'ERROR'):
        return False
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


# Built-in regex patterns for common metrics
BUILTIN_PATTERNS = {
    r"API calls?[:\s]+(\d+)": "api_call_count",
    r"(\d+)\s*API calls?": "api_call_count",
    r"(\d+)\s*rows?\s*written": "rows_written",
    r"wrote\s*(\d+)\s*rows?": "rows_written",
    r"score[:\s]+([\d.]+)": "score",
    r"accuracy[:\s]+([\d.]+)": "accuracy",
    r"(PASS|FAIL|pass|fail)": "validation_passed",
    r"validation[:\s]*(passed|failed|PASS|FAIL)": "validation_passed",
    r"errors?[:\s]+(\d+)": "error_count",
    r"(\d+)\s*errors?": "error_count",
    r"issues?[:\s]+(\d+)": "issue_count",
    r"(\d+)\s*issues?": "issue_count",
    r"tokens?[:\s]+(\d+)": "token_count",
    r"(\d+)\s*tokens?": "token_count",
    r"time[:\s]+([\d.]+)\s*s": "time_seconds",
    r"duration[:\s]+([\d.]+)": "duration_seconds",
    r"cost[:\s]+\$?([\d.]+)": "cost_dollars",
}


def extract_metrics(
    text: str,
    custom_extractors: list[dict] | None = None,
    elapsed_time: float | None = None
) -> dict[str, Any]:
    """
    Extract all measurable values from skill output.

    Args:
        text: The skill's stdout/stderr output
        custom_extractors: List of {"pattern": regex, "name": metric_name, "type": "int"|"float"|"bool"}
        elapsed_time: Wall clock time in seconds (if available)

    Returns:
        Dict of metric_name -> value
    """
    metrics = {}

    # 1. Add timing if provided
    if elapsed_time is not None:
        metrics["wall_time_seconds"] = round(elapsed_time, 2)

    # 2. Extract from JSON blocks
    for block in extract_json_blocks(text):
        flat = flatten_dict(block)
        for key, value in flat.items():
            if isinstance(value, (int, float, bool)):
                # Normalize key name
                key = key.lower().replace('-', '_').replace(' ', '_')
                metrics[key] = value

    # 3. Apply built-in regex patterns
    for pattern, name in BUILTIN_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = parse_value(match.group(1))
            # Handle boolean conversion for validation
            if name == "validation_passed":
                value = value in (True, "passed", "PASS", "pass")
            metrics[name] = value

    # 4. Apply custom extractors
    if custom_extractors:
        for extractor in custom_extractors:
            pattern = extractor.get("pattern")
            name = extractor.get("name")
            value_type = extractor.get("type", "auto")

            if not pattern or not name:
                continue

            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                raw_value = match.group(1) if match.lastindex else match.group(0)

                if value_type == "int":
                    metrics[name] = int(raw_value)
                elif value_type == "float":
                    metrics[name] = float(raw_value)
                elif value_type == "bool":
                    metrics[name] = raw_value.lower() in ('true', 'yes', 'pass', '1')
                else:
                    metrics[name] = parse_value(raw_value)

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Extract metrics from skill output")
    parser.add_argument("text", nargs="?", help="Skill output text (or use --file)")
    parser.add_argument("--file", "-f", help="Read output from file")
    parser.add_argument("--config", "-c", help="Config JSON with custom_extractors")
    parser.add_argument("--elapsed", "-e", type=float, help="Elapsed time in seconds")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    # Get input text
    if args.file:
        with open(args.file) as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    # Load custom extractors if provided
    custom_extractors = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
            custom_extractors = config.get("custom_extractors")

    # Extract metrics
    metrics = extract_metrics(text, custom_extractors, args.elapsed)

    # Output
    if args.pretty:
        print(json.dumps(metrics, indent=2))
    else:
        print(json.dumps(metrics))


if __name__ == "__main__":
    main()
