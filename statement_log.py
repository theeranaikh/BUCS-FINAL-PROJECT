import json

from model_test import RESULTS_FILE


def read_results(path=RESULTS_FILE):
    with open(path, encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def format_statement(result):
    input_text = json.dumps(result["input"], ensure_ascii=False)
    return (
        f'วันที่ {result["date"]} เวลา {result["time"]} '
        f'ทดสอบโมเดล {result["model"]} ด้วยอินพุต {input_text} '
        f'ได้ผลลัพธ์ {result["output"]}'
    )
