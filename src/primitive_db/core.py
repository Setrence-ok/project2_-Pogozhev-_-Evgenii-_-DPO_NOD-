# src/primitive_db/core.py
import os
from .utils import load_table_data, save_table_data, load_metadata


def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу
    """
    TYPES = {'int': 'integer', 'str': 'text', 'bool': 'boolean'}
    FILEPATH = f'data/{table_name}.json'

    # Проверяем существование таблицы
    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует")

    if os.path.exists(FILEPATH):
        raise ValueError(f"Файл для таблицы '{table_name}' уже существует")

    # Проверяем столбцы
    table_schema = {"ID": "integer"}  # ID всегда первый столбец

    for column in columns:
        if not isinstance(column, tuple) or len(column) != 2:
            raise ValueError("Каждый столбец должен быть кортежем (имя, тип)")

        column_name, column_type = column
        if column_type not in TYPES:
            raise ValueError(
                f"Тип '{column_type}' для столбца '{column_name}' не поддерживается. Используйте: int, str, bool")

        table_schema[column_name] = TYPES[column_type]

    # Добавляем таблицу в метаданные
    metadata[table_name] = table_schema

    # Создаем пустой файл для данных таблицы
    save_table_data(table_name, [])

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
    """
    Вставляет новую запись в таблицу
    """
    # Проверяем существование таблицы
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    table_schema = metadata[table_name]
    # Получаем все столбцы кроме ID
    columns = [col for col in table_schema.keys() if col != "ID"]

    # Проверяем количество значений
    if len(values) != len(columns):
        raise ValueError(
            f"Неверное количество значений. Ожидается {len(columns)} ({', '.join(columns)}), получено {len(values)}")

    # Валидируем типы данных
    validated_values = []
    for i, col_name in enumerate(columns):
        expected_type = table_schema[col_name]
        value = values[i]

        # Валидация типов
        if expected_type == "integer":
            try:
                if isinstance(value, str):
                    value = int(value) if value.isdigit() else value
                if not isinstance(value, int):
                    raise ValueError(f"Неверный тип для столбца '{col_name}'. Ожидается integer")
            except ValueError:
                raise ValueError(f"Неверное значение для столбца '{col_name}'. Ожидается целое число")

        elif expected_type == "boolean":
            if isinstance(value, str):
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                else:
                    raise ValueError(f"Неверное значение для столбца '{col_name}'. Ожидается true/false")
            elif not isinstance(value, bool):
                raise ValueError(f"Неверный тип для столбца '{col_name}'. Ожидается boolean")

        elif expected_type == "text" and not isinstance(value, str):
            value = str(value)

        validated_values.append(value)

    # Создаем новую запись с ID на первом месте
    new_record = {"ID": None}  # ID будет установлен позже
    for i, col_name in enumerate(columns):
        new_record[col_name] = validated_values[i]

    return new_record


def select(table_data, where_clause=None):
    """
    Выбирает записи из таблицы
    """
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


def update(table_data, set_clause, where_clause):
    """
    Обновляет записи в таблице
    """
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


def delete(table_data, where_clause):
    """
    Удаляет записи из таблицы
    """
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
