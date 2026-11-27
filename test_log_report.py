import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from log_report import parse_log_line, print_report, read_log


class LogReportTest(unittest.TestCase):
    def test_report_groups_valid_records_and_warns_about_invalid_line(self):
        raw_log = (
            '2026-11-27T18:17:33|word-count|1|1|"ทดสอบ"\n'
            'invalid\n'
            '2026-11-27T18:18:04|char-count|3|3|"A|B"\n'
            '2026-11-27T18:18:12|char-count|2|3|"ABC"\n'
        )
        report, warnings = StringIO(), StringIO()
        with TemporaryDirectory() as directory:
            path = Path(directory) / "results.txt"
            path.write_text(raw_log, encoding="utf-8")
            with redirect_stdout(report), redirect_stderr(warnings):
                print_report(read_log(path))

        self.assertIn("บรรทัดที่ 2", warnings.getvalue())
        self.assertIn("อ่านผลทดสอบได้ 3 รายการ", report.getvalue())
        summary = report.getvalue().split("สรุปตามโมเดล\n", 1)[1].split("\n\n", 1)[0]
        header, _, first, second = summary.splitlines()
        self.assertEqual([cell.strip() for cell in header.split("|")], ["โมเดล", "ผ่าน", "ไม่ผ่าน"])
        self.assertEqual([cell.strip() for cell in first.split("|")], ["char-count", "1", "1"])
        self.assertEqual([cell.strip() for cell in second.split("|")], ["word-count", "1", "0"])
        details = report.getvalue().splitlines()[-3:]
        passed = [cell.strip() for cell in details[1].split(" | ", 6)]
        failed = [cell.strip() for cell in details[2].split(" | ", 6)]
        self.assertEqual(passed, ["2026-11-27", "18:18:04", "char-count", "3", "3", "ผ่าน", '"A|B"'])
        self.assertEqual(failed, ["2026-11-27", "18:18:12", "char-count", "2", "3", "ไม่ผ่าน", '"ABC"'])

    def test_report_limits_details_but_summarizes_all_records(self):
        records = [
            parse_log_line(f'2026-11-27T18:17:33|word-count|1|1|"case-{number}"')
            for number in range(21)
        ]
        report = StringIO()
        print_report(records, file=report, limit=20)

        lines = report.getvalue().splitlines()
        summary_row = lines[6]
        self.assertEqual([cell.strip() for cell in summary_row.split("|")], ["word-count", "21", "0"])
        heading = lines.index("รายละเอียดการทดสอบ (20 จาก 21 รายการ)")
        self.assertEqual(len(lines[heading + 3:]), 20)
        self.assertIn('"case-19"', lines[-1])

        full_report = StringIO()
        print_report(records, file=full_report)
        full_lines = full_report.getvalue().splitlines()
        heading = full_lines.index("รายละเอียดการทดสอบ (21 จาก 21 รายการ)")
        self.assertEqual(len(full_lines[heading + 3:]), 21)
        self.assertIn('"case-20"', full_lines[-1])
