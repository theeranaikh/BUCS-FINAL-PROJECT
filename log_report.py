import json
import sys
from datetime import datetime
from pathlib import Path
from unicodedata import category, east_asian_width


LOG_FILE = Path(__file__).with_name("results.txt")
REPORT_FILE = LOG_FILE.with_name("report.txt")


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


def detail_row(record):
    tested_at = record["timestamp"]
    status = "ผ่าน" if test_passed(record) else "ไม่ผ่าน"
    return (
        f"{tested_at:%Y-%m-%d}",
        f"{tested_at:%H:%M:%S}",
        record["model"],
        str(record["output"]),
        str(record["expected"]),
        status,
        json.dumps(record["input"], ensure_ascii=False),
    )


def print_table(headers, rows, *, file=None, right_aligned=()):
    def display_width(text):
        # shortcut: estimate character widths, use grapheme widths if model names need emoji clusters.
        return sum(
            2 if east_asian_width(character) in {"W", "F"} else 1
            for character in text
            if category(character) not in {"Mn", "Me", "Cf"}
        )

    values = [headers, *rows]
    widths = [max(map(display_width, column)) for column in zip(*values)]
    if len(headers) - 1 not in right_aligned:
        widths[-1] = display_width(headers[-1])
    for row_number, row in enumerate(values):
        cells = []
        for index, text in enumerate(row):
            padding = " " * (widths[index] - display_width(text))
            cells.append(padding + text if index in right_aligned else text + padding)
        print(" | ".join(cells).rstrip(), file=file)
        if row_number == 0:
            print("-+-".join("-" * width for width in widths), file=file)


def print_report(records, file=None, *, limit=None):
    print("รายงานผลการทดสอบโมเดล", file=file)
    print(f"อ่านผลทดสอบได้ {len(records)} รายการ", file=file)
    if not records:
        return

    print("\nสรุปตามโมเดล", file=file)
    summary = [
        (model, str(counts["passed"]), str(counts["failed"]))
        for model, counts in sorted(summarize_by_model(records).items())
    ]
    print_table(("โมเดล", "ผ่าน", "ไม่ผ่าน"), summary, file=file, right_aligned=(1, 2))

    details = records[:limit]
    print(f"\nรายละเอียดการทดสอบ ({len(details)} จาก {len(records)} รายการ)", file=file)
    print_table(
        ("วันที่", "เวลา", "โมเดล", "ผลลัพธ์", "คาดไว้", "สถานะ", "อินพุต"),
        [detail_row(record) for record in details],
        file=file,
        right_aligned=(3, 4),
    )


if __name__ == "__main__":
    records = read_log()
    with REPORT_FILE.open("w", encoding="utf-8") as report:
        print_report(records, file=report)
    print_report(records, limit=20)
