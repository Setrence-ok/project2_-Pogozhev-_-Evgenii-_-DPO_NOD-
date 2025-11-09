# src/primitive_db/utils.py

import json
import os

DATA_DIR = "data"


def ensure_data_dir():
    """Создает директорию data, если она не существует"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_table_data(table_name):
    """
    Загружает данные таблицы из JSON-файла
    """
    ensure_data_dir()
    filename = os.path.join(DATA_DIR, f"{table_name}.json")

    if not os.path.exists(filename):
        return []

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_table_data(table_name, data):
    """
    Сохраняет данные таблицы в JSON-файл
    """
    ensure_data_dir()
    filename = os.path.join(DATA_DIR, f"{table_name}.json")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_metadata():
    """
    Загружает метаданные таблиц
    """
    ensure_data_dir()
    filename = os.path.join(DATA_DIR, "metadata.json")

    if not os.path.exists(filename):
        return {}

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_metadata(metadata):
    """
    Сохраняет метаданные таблиц
    """
    ensure_data_dir()
    filename = os.path.join(DATA_DIR, "metadata.json")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
