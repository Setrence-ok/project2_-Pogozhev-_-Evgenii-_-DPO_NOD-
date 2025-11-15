# src/primitive_db/utils.py

import json
import os

DATA_DIR = "data"
METADATA = "db_meta.json"


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_table_data(table_name):
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
    ensure_data_dir()
    filename = os.path.join(DATA_DIR, f"{table_name}.json")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_metadata():
    ensure_data_dir()
    filename = os.path.join(DATA_DIR, METADATA)

    if not os.path.exists(filename):
        return {}

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_metadata(metadata):
    ensure_data_dir()
    filename = os.path.join(DATA_DIR, METADATA)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
