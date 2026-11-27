import json
import sys
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
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


def print_report(records, file=None, *, limit=None, numbered=False):
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
    headers = ("วันที่", "เวลา", "โมเดล", "ผลลัพธ์", "คาดไว้", "สถานะ", "อินพุต")
    rows = [detail_row(record) for record in details]
    if numbered:
        rows = [(str(number), *row) for number, row in enumerate(rows, start=1)]
        print_table(("เลข", *headers), rows, file=file, right_aligned=(0, 4, 5))
    else:
        print_table(headers, rows, file=file, right_aligned=(3, 4))


def main():
    records = []
    while True:
        print(f"\nจัดการ Log ({len(records)} รายการ)")
        print("1 เปิดไฟล์ log   2 ดูรายงาน   3 เพิ่ม   4 ลบ   5 แก้ไข   0 ออก")
        try:
            choices = input("เลือกเมนู > ").strip().split(maxsplit=1)
            if not choices:
                continue
            command = choices[0]
            argument = choices[1] if len(choices) == 2 else ""
            if command == "0":
                return
            if command == "2":
                print_report(records, limit=20, numbered=True)
                continue

            if command == "1":
                filename = argument or input("ชื่อไฟล์ log > ").strip()
                if not filename:
                    raise ValueError("กรุณาระบุชื่อไฟล์ log")
                path = Path(filename.strip('"')).expanduser()
                if path.resolve() == REPORT_FILE.resolve():
                    raise ValueError("กรุณาเลือกไฟล์ log ดิบ")
                updated = read_log(path)
            elif command in {"3", "4", "5"}:
                updated = records.copy()
                if command in {"4", "5"}:
                    if not records:
                        raise ValueError("ยังไม่มีรายการให้ลบหรือแก้ไข")
                    number = int(argument or input("เลขรายการจากรายงาน > "))
                    if not 1 <= number <= len(records):
                        raise ValueError(f"กรุณาใช้เลขรายการ 1 ถึง {len(records)}")
                    if command == "4":
                        del updated[number - 1]

                if command in {"3", "5"}:
                    default_time = (
                        records[number - 1]["timestamp"] if command == "5" else datetime.now()
                    ).isoformat(timespec="seconds")
                    timestamp = input(f"วันและเวลา [{default_time}] > ").strip() or default_time
                    model = input("ชื่อโมเดล > ").strip()
                    output = input("ผลลัพธ์ (จำนวนเต็ม) > ").strip()
                    expected = input("ค่าที่คาดไว้ (จำนวนเต็ม) > ").strip()
                    text = json.dumps(input("อินพุต > "), ensure_ascii=False)
                    record = parse_log_line(f"{timestamp}|{model}|{output}|{expected}|{text}")
                    if command == "3":
                        updated.append(record)
                    else:
                        updated[number - 1] = record
            else:
                raise ValueError("กรุณาเลือกเมนู 0 ถึง 5")

            with TemporaryDirectory(dir=REPORT_FILE.parent) as directory:
                temporary_report = Path(directory) / REPORT_FILE.name
                with temporary_report.open("w", encoding="utf-8") as report:
                    print_report(updated, file=report, numbered=True)
                temporary_report.replace(REPORT_FILE)
            records = updated
            print_report(records, limit=20, numbered=True)
            print(f"บันทึกรายงานใน {REPORT_FILE.name} แล้ว")
        except (OSError, ValueError) as error:
            print(f"ทำรายการไม่สำเร็จ ({error})")
        except (EOFError, KeyboardInterrupt):
            print()
            return


if __name__ == "__main__":
    main()
