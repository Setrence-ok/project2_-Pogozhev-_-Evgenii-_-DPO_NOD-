# src/primitive_db/core.py
import os

from .decorators import confirm_action, handle_db_errors, log_time
from .utils import METADATA, save_table_data


def create_table(metadata, table_name, columns):
    TYPES = {'int': 'integer', 'str': 'text', 'bool': 'boolean'}
    FILEPATH = f'data/{table_name}.json'

    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует")

    if os.path.exists(FILEPATH):
        raise ValueError(f"Файл для таблицы '{table_name}' уже существует")

    table_schema = {"ID": "integer"}  # ID всегда первый столбец

    for column in columns:
        if not isinstance(column, tuple) or len(column) != 2:
            raise ValueError("Каждый столбец должен быть кортежем (имя, тип)")

        column_name, column_type = column
        if column_type not in TYPES:
            raise ValueError(
                f"Тип '{column_type}' для столбца '{column_name}' не поддерживается. "
                f"Используйте: int, str, bool")

        table_schema[column_name] = TYPES[column_type]

    metadata[table_name] = table_schema

    save_table_data(table_name, [])

    return metadata


@handle_db_errors
@confirm_action("удаление таблицы", None)
def drop_table(metadata, table_name):
    FILEPATH = f'data/{table_name}.json'
    if not os.path.exists(FILEPATH):
        raise ValueError(f"Ошибка: Таблица '{table_name}' не существует")
    del metadata[table_name]
    os.remove(FILEPATH)
    print(f"Таблица '{table_name}' успешно удалена.")
    return metadata


def list_tables(directory):
    files = os.listdir(directory)
    if files:
        for filename in files:
            if filename != METADATA:
                filename = os.path.splitext(filename)[0]
                print(f"- '{filename}'")
    else:
        raise ValueError("Ошибка: Таблиц в файле не найдено!")


@handle_db_errors
def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    table_schema = metadata[table_name]
    columns = [col for col in table_schema.keys() if col != "ID"]

    if len(values) != len(columns):
        raise ValueError(
            f"Неверное количество значений. Ожидается {len(columns)} "
            f"({', '.join(columns)}), получено {len(values)}")

    validated_values = []
    for i, col_name in enumerate(columns):
        expected_type = table_schema[col_name]
        value = values[i]

        if expected_type == "integer":
            try:
                if isinstance(value, str):
                    value = int(value) if value.isdigit() else value
                if not isinstance(value, int):
                    raise ValueError(f"Неверный тип для столбца '{col_name}'. "
                                     f"Ожидается integer")
            except ValueError:
                raise ValueError(f"Неверное значение для столбца '{col_name}'. "
                                 f"Ожидается целое число")

        elif expected_type == "boolean":
            if isinstance(value, str):
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                else:
                    raise ValueError(f"Неверное значение для столбца '{col_name}'. "
                                     f"Ожидается true/false")
            elif not isinstance(value, bool):
                raise ValueError(f"Неверный тип для столбца '{col_name}'. "
                                 f"Ожидается boolean")

        elif expected_type == "text" and not isinstance(value, str):
            value = str(value)

        validated_values.append(value)

    new_record = {"ID": None}
    for i, col_name in enumerate(columns):
        new_record[col_name] = validated_values[i]

    return new_record


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data

    filtered_data = []
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or str(record[column]) != str(value):
                match = False
                break

        if match:
            filtered_data.append(record)

    return filtered_data


@handle_db_errors
def update(table_data, set_clause, where_clause):
    updated_count = 0

    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or str(record[column]) != str(value):
                match = False
                break

        if match:
            for column, new_value in set_clause.items():
                if column in record and column != "ID":
                    record[column] = new_value
            updated_count += 1

    return table_data, updated_count


@handle_db_errors
@confirm_action("удаление записи", return_=(None, 0))
def delete(table_data, where_clause):
    if where_clause is None:
        return table_data, 0

    new_data = []
    deleted_count = 0

    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or str(record[column]) != str(value):
                match = False
                break

        if not match:
            new_data.append(record)
        else:
            deleted_count += 1

    return new_data, deleted_count
