# src/primitive_db/utils.py

import json
import os


def load_metadata(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    FILEPATH = f'data/{table_name}.json'
    if not os.path.exists(FILEPATH):
        return {}

    try:
        with open(FILEPATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Ошибка: Файл '{FILEPATH}' содержит некорректный JSON.")
        return {}


def save_table_data(table_name, data):
    FILEPATH = f'data/{table_name}.json'

    with open(FILEPATH, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
