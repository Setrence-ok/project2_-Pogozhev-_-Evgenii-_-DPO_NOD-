# src/primitive_db/core.py
import os
from .utils import load_table_data, save_table_data


def create_table(metadata, table_name, columns):
    TYPES = {'int': int, 'str': str, 'bool': bool}
    FILEPATH = f'data/{table_name}.json'
    if os.path.exists(FILEPATH):
        raise ValueError(f"Ошибка: Таблица '{table_name}' уже существует")
    for column in columns:
        if not isinstance(column, tuple) or len(column) != 2:
            raise ValueError("Каждый столбец должен быть кортежем (имя, тип).")
        column_name, column_type = column
        if column_type not in TYPES:
            raise ValueError(f"Ошибка! Тип '{column_type}' для столбца '{column_name}' не поддерживается.")

    id_column = ('ID', 'int')
    columns.insert(0, id_column)

    metadata[table_name] = {
        'columns': [(col[0], str(col[1])) for col in columns]
    }

    return metadata


def drop_table(metadata, table_name):
    FILEPATH = f'data/{table_name}.json'
    if not os.path.exists(FILEPATH):
        raise ValueError(f"Ошибка: Таблица '{table_name}' не существует")
    del metadata[table_name]
    os.remove(FILEPATH)
    return metadata


def list_tables(directory):
    files = os.listdir(directory)
    if files:
        for filename in files:
            filename = os.path.splitext(filename)[0]
            print(f"- '{filename}'")
    else:
        raise ValueError("Ошибка: Таблиц в файле не найдено!")


def insert(metadata, table_name, values):
    FILEPATH = f'data/{table_name}.json'
    columns = metadata[table_name]['columns']

    if not os.path.exists(FILEPATH):
        raise ValueError(f"Ошибка: Таблица '{table_name}' не существует.")

    expected_column_count = len(columns) - 1
    if len(values) != expected_column_count:
        raise ValueError(f"Ошибка: Необходимое количество значений: {expected_column_count}, получено: {len(values)}.")

    processed_values = []

    for i, (column_name, column_type) in enumerate(columns[1:]):
        if column_type == 'int':
            processed_values.append(int(values[i]))
        elif column_type == 'str':
            processed_values.append(str(values[i]))
        elif column_type == 'bool':
            processed_values.append(bool(values[i]))
        else:
            raise ValueError(f"Неподдерживаемый тип данных: {column_type}")

    current_data = load_table_data(table_name)
    table_data = current_data.get(table_name, {})
    records = table_data.get('data', [])

    new_id = max([record.get('ID', 0) for record in records], default=0) + 1
    new_record = {'ID': new_id}

    for i, (column_type, column_name) in enumerate(columns[1:]):
        new_record[column_type] = values[i]

    if 'data' not in current_data[table_name]:
        current_data[table_name]['data'] = []
        current_data[table_name]['data'].append(new_record)
    else:
        current_data[table_name]['data'].append(new_record)
    save_table_data(table_name, current_data)

    return current_data
