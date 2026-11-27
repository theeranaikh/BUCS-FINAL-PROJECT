import argparse
import json
from datetime import datetime
from pathlib import Path


RESULTS_FILE = Path(__file__).with_name("results.txt")


def count_words(input_text):
    return len(input_text.split())


def create_result(input_text):
    tested_at = datetime.now()
    return {
        "date": tested_at.date().isoformat(),
        "time": tested_at.strftime("%H:%M:%S"),
        "model": "word-count",
        "input": input_text,
        "output": count_words(input_text),
    }


def save_result(result, path=RESULTS_FILE):
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(result, ensure_ascii=False) + "\n")


def run_test(input_text, path=RESULTS_FILE):
    save_result(create_result(input_text), path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the word-count model and save the result.")
    parser.add_argument("text", help="Text to test")
    args = parser.parse_args()
    run_test(args.text)
