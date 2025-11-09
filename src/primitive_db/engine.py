# src/primitive_db/engine.py
import shlex
from .decorators import create_cacher, log_time
from .core import create_table, drop_table, list_tables, insert, delete, select, update
from .utils import load_metadata, save_metadata, load_table_data, save_table_data
from .parser import parse_where_clause, parse_set_clause, parse_values
from prettytable import PrettyTable


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
          "where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run_create_table(metadata, args):
    if len(args) < 3:
        print("Использование: create_table <имя_таблицы> <столбец1:тип> ...")
        return

    table_name = args[1]
    columns = []

    for column in args[2:]:
        col_parts = column.split(':')
        if len(col_parts) != 2:
            print(f"Ошибка в столбце '{column}'. Формат: <column_name>:<type>")
            return
        columns.append((col_parts[0], col_parts[1]))

    try:
        updated_metadata = create_table(metadata, table_name, columns)
        save_metadata(updated_metadata)
        column_descriptions = ', '.join([f"{col[0]}:{col[1]}" for col in columns])
        print(f"Таблица '{table_name}' успешно создана со столбцами: {column_descriptions}")
    except ValueError as ve:
        print(ve)


def run_list_tables():
    direct = "data"
    try:
        list_tables(direct)
    except ValueError as ve:
        print(ve)


def run_drop_table(metadata, args):
    if len(args) < 2:
        print("Использование: drop_table <table_name>")
        return

    table_name = args[1]

    try:
        metadata = drop_table(metadata, table_name)
        if metadata is not None:
            save_metadata(metadata)
    except ValueError as ve:
        print(ve)


@log_time
def run_insert(metadata, args):
    if len(args) < 4 or args[1] != "into" or args[3] != "values":
        print("Ошибка: Неверный формат команды INSERT. Используйте: insert into <таблица> values (<значения>)")
        return

    table_name = args[2]
    values_str = " ".join(args[4:])

    try:
        values = parse_values(values_str)
        table_data = load_table_data(table_name)
        new_record = insert(metadata, table_name, values)

        if table_data:
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


def run_select(args, cache):
    if len(args) < 2 or args[1] != "from":
        print("Ошибка: Неверный формат команды SELECT. Используйте: select from <таблица> [where <условие>]")
        return

    table_name = args[2]
    where_clause = None

    if "where" in args:
        where_index = args.index("where")
        where_condition = " ".join(args[where_index + 1:])
        where_clause = parse_where_clause(where_condition)

    try:
        table_data = load_table_data(table_name)
        cache_key = f"select.{table_name}.{str(where_clause)}"

        def get_selected_data():
            return select(table_data, where_clause)
        result_data = cache(cache_key, get_selected_data)

        if not result_data:
            print("Записи не найдены.")
            return

        metadata = load_metadata()
        if table_name in metadata:
            all_fields = list(metadata[table_name].get('columns', []))
        else:
            all_fields = list(result_data[0].keys())
            if "ID" in all_fields:
                all_fields.remove("ID")
                all_fields = ["ID"] + all_fields

        table = PrettyTable()
        table.field_names = all_fields

        for record in result_data:
            row = [record.get(field, "") for field in all_fields]
            table.add_row(row)

        print(table)

    except ValueError as ve:
        print(ve)


def run_update(args):
    if len(args) < 5 or args[2] != "set" or "where" not in args:
        print(
            "Ошибка: Неверный формат команды UPDATE. Используйте: update <таблица> set <присваивания> where <условие>")
        return

    table_name = args[1]
    set_index = args.index("set")
    where_index = args.index("where")

    set_condition = " ".join(args[set_index + 1:where_index])
    where_condition = " ".join(args[where_index + 1:])

    try:
        table_data = load_table_data(table_name)

        set_clause = parse_set_clause(set_condition)
        where_clause = parse_where_clause(where_condition)

        updated_data, updated_count = update(table_data, set_clause, where_clause)

        save_table_data(table_name, updated_data)

        print(f"Запись(и) в таблице '{table_name}' успешно обновлена(ы). Обновлено записей: {updated_count}")

    except ValueError as ve:
        print(ve)


def run_delete(args):
    if len(args) < 4 or args[1] != "from" or args[3] != "where":
        print("Ошибка: Неверный формат команды DELETE. Используйте: delete from <таблица> where <условие>")
        return

    table_name = args[2]
    where_condition = " ".join(args[4:])

    try:
        table_data = load_table_data(table_name)

        where_clause = parse_where_clause(where_condition)

        result = delete(table_data, where_clause)
        if result is None:
            return
        new_data, deleted_count = result
        if deleted_count > 0:
            save_table_data(table_name, new_data)
            print(f"Запись(и) успешно удалена(ы) из таблицы '{table_name}'. Удалено записей: {deleted_count}")

    except ValueError as ve:
        print(ve)


def run_info(args):
    if len(args) < 1:
        print("Ошибка: Укажите имя таблицы. Используйте: info <таблица>")
        return

    table_name = args[1]

    try:
        metadata = load_metadata()

        if table_name not in metadata:
            print(f"Ошибка: Таблица '{table_name}' не существует")
            return

        table_schema = metadata[table_name]
        table_data = load_table_data(table_name)

        print(f"Информация о таблице '{table_name}':")
        print(f"Количество записей: {len(table_data)}")
        print("Структура таблицы:")

        schema_table = PrettyTable()
        schema_table.field_names = ["Столбец", "Тип данных"]

        for column, data_type in table_schema.items():
            schema_table.add_row([column, data_type])

        print(schema_table)

    except ValueError as ve:
        print(ve)


def run():
    metadata = load_metadata()
    cache = create_cacher()

    while True:
        user_input = input("Введите команду: ")
        args = shlex.split(user_input)

        if not args:
            continue
        args = shlex.split(user_input)
        command = args[0]

        if command == "create_table":
            run_create_table(metadata, args)

        elif command == "list_tables":
            run_list_tables()

        elif command == "drop_table":
            run_drop_table(metadata, args)

        elif command == "insert":
            run_insert(metadata, args)

        elif command == "select":
            run_select(args, cache)

        elif command == "update":
            run_update(args)

        elif command == "delete":
            run_delete(args)

        elif command == "info":
            run_info(args)

        elif command == "help":
            print_help()

        elif command == "exit":
            print("Выход из программы.")
            break

        else:
            print(f"Ошибка: Функции '{command}' нет. Попробуйте снова!")
