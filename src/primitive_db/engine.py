# src/primitive_db/engine.py
import prompt
import shlex
from .utils import load_metadata, save_metadata
from .core import create_table, drop_table, list_tables


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
                metadata = create_table(metadata, table_name, columns)
                save_metadata(filepath, metadata)
                column_descriptions = ', '.join([f"{col[0]}:{col[1]}" for col in metadata[table_name]['columns']])
                print(f"Таблица '{table_name}' успешно создана со столбцами: {column_descriptions}")
            except ValueError as ve:
                print(ve)

        elif command == "list_tables":
            try:
                list_tables(metadata)
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

        elif command == "help":
            print_help()

        elif command == "exit":
            print("Выход из программы.")
            break

        else:
            print("Ошибка: Неизвестная команда.")