import json
from datetime import datetime


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
