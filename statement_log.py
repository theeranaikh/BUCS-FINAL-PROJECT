import json

from model_test import RESULTS_FILE


def read_results(path=RESULTS_FILE):
    with open(path, encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]
