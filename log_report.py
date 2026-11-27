import json
import sys
from datetime import datetime
from pathlib import Path


LOG_FILE = Path(__file__).with_name("results.txt")


def parse_log_line(line):
    timestamp, model, output, expected, raw_input = line.split("|", 4)
    input_text = json.loads(raw_input)
    if not model.strip() or not isinstance(input_text, str):
        raise ValueError("ชื่อโมเดลหรืออินพุตไม่ถูกต้อง")
    return {
        "timestamp": datetime.fromisoformat(timestamp),
        "model": model,
        "input": input_text,
        "output": int(output),
        "expected": int(expected),
    }


def read_log(path=LOG_FILE):
    path = Path(path)
    records = []
    with open(path, encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                records.append(parse_log_line(line))
            except ValueError:
                print(f"ข้ามบรรทัดที่ {number} ใน {path.name} เพราะรูปแบบไม่ถูกต้อง", file=sys.stderr)
    return records


def test_passed(record):
    return record["output"] == record["expected"]


def summarize_by_model(records):
    summary = {}
    for record in records:
        counts = summary.setdefault(record["model"], {"passed": 0, "failed": 0})
        status = "passed" if test_passed(record) else "failed"
        counts[status] += 1
    return summary
