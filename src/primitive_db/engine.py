# src/primitive_db/engine.py
import shlex

from .core import create_table, drop_table, list_tables, insert
from .utils import load_metadata, save_metadata, load_table_data, save_table_data


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    filepath = 'db_meta.json'
    metadata = load_metadata(filepath)

    while True:
        user_input = input("Введите команду: ")
        args = shlex.split(user_input)

        if not args:
            continue

        command = args[0]

        if command == "create_table":
            if len(args) < 3:
                print("Использование: create_table <имя_таблицы> <столбец1:тип> ...")
                continue

            table_name = args[1]
            columns = []

            for column in args[2:]:
                col_parts = column.split(':')
                if len(col_parts) != 2:
                    print(f"Ошибка в столбце '{column}'. Формат: <column_name>:<type>")
                    break
                columns.append((col_parts[0], col_parts[1]))

            try:
                filepath2 = load_table_data(f'data/{table_name}.json')
                metadata = create_table(filepath2, table_name, columns)
                save_table_data(table_name, metadata)
                save_metadata(filepath, metadata)
                column_descriptions = ', '.join([f"{col[0]}:{col[1]}" for col in metadata[table_name]['columns']])
                print(f"Таблица '{table_name}' успешно создана со столбцами: {column_descriptions}")
            except ValueError as ve:
                print(ve)

        elif command == "list_tables":
            direct = "data"
            try:
                list_tables(direct)
            except ValueError as ve:
                print(ve)

        elif command == "drop_table":
            if len(args) < 2:
                print("Использование: drop_table <table_name>")
                continue

            table_name = args[1]

            try:
                metadata = drop_table(metadata, table_name)
                save_metadata(filepath, metadata)
                print(f"Таблица '{table_name}' успешно удалена.")
            except ValueError as ve:
                print(ve)
        elif command == "insert":
            if len(args) < 4 or args[3] != "values":
                print("Использование: insert into <имя_таблицы> values (<значение1>, <значение2>, ...)")
                continue
            try:
                table_name = args[2]
                values = args[4:]
                values = [v.strip(', ') for v in values]
                processed_values = []
                for value in values:
                    if value.isdigit():
                        processed_values.append(int(value))
                    elif value.lower() == 'true':
                        processed_values.append(True)
                    elif value.lower() == 'false':
                        processed_values.append(False)
                    else:
                        processed_values.append(value.strip("'"))
                print("Полученные значения:", values)
                print(values)
                insert(metadata, table_name, processed_values)
            except ValueError as ve:
                print(ve)

        elif command == "help":
            print_help()

        elif command == "exit":
            print("Выход из программы.")
            break

        else:
            print(f"Ошибка: Функции '{command}' нет. Попробуйте снова!")