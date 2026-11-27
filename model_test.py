from datetime import datetime


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
