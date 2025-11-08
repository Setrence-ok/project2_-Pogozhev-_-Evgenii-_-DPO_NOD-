# src/primitive_db/core.py
import os


def create_table(metadata, table_name, columns):
    TYPES = {'int': int, 'str': str, 'bool': bool}
    filepath = f'data/{table_name}.json'
    if os.path.exists(filepath):
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
    if table_name not in metadata:
        raise ValueError(f"Ошибка: Таблица '{table_name}' не существует.")

    del metadata[table_name]
    return metadata


def list_tables(metadata):
    if metadata:
        for name in metadata.keys():
            print(f"- '{name}'")
    else:
        raise ValueError("Ошибка: Таблиц в файле не найдено!")
