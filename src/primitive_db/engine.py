# src/primitive_db/engine.py
import shlex
import sys
from .core import create_table, drop_table, list_tables, insert
from .utils import load_metadata, save_metadata, load_table_data, save_table_data
from .parser import parse_where_clause, parse_set_clause, parse_values


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
    metadata = load_metadata()

    while True:
        user_input = input("Введите команду: ")
        args = shlex.split(user_input)

        if not args:
            continue
        args = shlex.split(user_input)
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
                    continue
                columns.append((col_parts[0], col_parts[1]))

            try:
                updated_metadata = create_table(metadata, table_name, columns)
                save_metadata(updated_metadata)
                column_descriptions = ', '.join([f"{col[0]}:{col[1]}" for col in columns])
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
                save_metadata(metadata)
                print(f"Таблица '{table_name}' успешно удалена.")
            except ValueError as ve:
                print(ve)
        elif command == "insert":
            """Обрабатывает команду INSERT"""
            if len(args) < 4 or args[1] != "into" or args[3] != "values":
                print("Ошибка: Неверный формат команды INSERT. Используйте: insert into <таблица> values (<значения>)")
                continue

            table_name = args[2]
            values_str = " ".join(args[4:])

            try:
                values = parse_values(values_str)
                table_data = load_table_data(table_name)
                metadata = load_metadata()

                new_record = insert(metadata, table_name, values)

                # Генерируем ID
                if table_data:
                    # Фильтруем записи с None и извлекаем ID
                    valid_ids = []
                    for record in table_data:
                        if record is not None and isinstance(record, dict) and "ID" in record:
                            valid_ids.append(record["ID"])

                    if valid_ids:
                        max_id = max(valid_ids)
                        new_record["ID"] = max_id + 1
                    else:
                        new_record["ID"] = 1
                else:
                    new_record["ID"] = 1

                table_data.append(new_record)
                save_table_data(table_name, table_data)

                print(f'Запись с ID={new_record["ID"]} успешно добавлена в таблицу "{table_name}".')

            except ValueError as ve:
                print(ve)

        elif command == "select":


        elif command == "update":


        elif command == "delete":


        elif command == "help":
            print_help()

        elif command == "exit":
            print("Выход из программы.")
            break

        else:
            print(f"Ошибка: Функции '{command}' нет. Попробуйте снова!")