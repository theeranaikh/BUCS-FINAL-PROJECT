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


def print_statements(path=RESULTS_FILE):
    for result in read_results(path):
        print(format_statement(result))


if __name__ == "__main__":
    print_statements()
