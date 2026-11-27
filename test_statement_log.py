from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from model_test import run_test
from statement_log import format_statement, read_results


class StatementLogTest(unittest.TestCase):
    def test_new_results_append_to_text_log(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "results.txt"
            run_test("Hello world", path)
            run_test("ทดสอบ\nโมเดล Python", path)
            first, second = read_results(path)

        self.assertEqual((first["input"], first["output"]), ("Hello world", 2))
        self.assertEqual((second["input"], second["output"]), ("ทดสอบ\nโมเดล Python", 3))
        self.assertEqual(
            format_statement(second),
            f'วันที่ {second["date"]} เวลา {second["time"]} '
            'ทดสอบโมเดล word-count ด้วยอินพุต "ทดสอบ\\nโมเดล Python" ได้ผลลัพธ์ 3',
        )
