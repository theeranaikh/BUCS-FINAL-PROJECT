import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from log_report import print_report, read_log


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
        self.assertIn("char-count | ผ่าน 1 | ไม่ผ่าน 1", report.getvalue())
        self.assertIn("word-count | ผ่าน 1 | ไม่ผ่าน 0", report.getvalue())
        self.assertIn('"A|B" ได้ผลลัพธ์ 3 คาดไว้ 3 [ผ่าน]', report.getvalue())
        self.assertIn('"ABC" ได้ผลลัพธ์ 2 คาดไว้ 3 [ไม่ผ่าน]', report.getvalue())
