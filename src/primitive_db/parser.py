# src/primitive_db/parser.py

def parse_where_clause(where_condition):
    """
    Парсит условие WHERE в формате "столбец = значение"
    Возвращает словарь {столбец: значение}
    """
    if not where_condition:
        return None

    # Убираем лишние пробелы
    condition = where_condition.strip()

    # Разделяем по "="
    if "=" not in condition:
        raise ValueError("Некорректный формат условия WHERE. Используйте: "
                         "столбец = значение")

    parts = condition.split("=", 1)
    column = parts[0].strip()
    value_str = parts[1].strip()

    # Парсим значение
    value = parse_value(value_str)

    return {column: value}


def parse_set_clause(set_condition):
    """
    Парсит условие SET в формате "столбец1 = значение1, столбец2 = значение2"
    Возвращает словарь {столбец: значение}
    """
    if not set_condition:
        return {}

    set_dict = {}
    assignments = set_condition.split(",")

    for assignment in assignments:
        assignment = assignment.strip()
        if "=" not in assignment:
            raise ValueError(f"Некорректный формат присваивания: {assignment}")

        parts = assignment.split("=", 1)
        column = parts[0].strip()
        value_str = parts[1].strip()

        value = parse_value(value_str)
        set_dict[column] = value

    return set_dict


def parse_value(value_str):
    """
    Парсит строковое значение в соответствующий тип данных
    """
    # Убираем кавычки если есть
    if (value_str.startswith('"') and value_str.endswith('"')) or \
            (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    # Булевы значения
    if value_str.lower() == "true":
        return True
    elif value_str.lower() == "false":
        return False

    # Числа
    try:
        return int(value_str)
    except ValueError:
        try:
            return float(value_str)
        except ValueError:
            pass

    # Если ничего не подошло, возвращаем как строку
    return value_str


def parse_values(values_str):
    """
    Парсит строку значений в формате "(значение1, значение2, ...)"
    """
    # Убираем скобки и лишние пробелы
    values_str = values_str.strip()
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1]

    # Разделяем значения
    values = []
    current_value = ""
    in_quotes = False
    quote_char = None

    for char in values_str:
        if char in ['"', "'"] and not in_quotes:
            in_quotes = True
            quote_char = char
            current_value += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            current_value += char
        elif char == "," and not in_quotes:
            values.append(current_value.strip())
            current_value = ""
        else:
            current_value += char

    if current_value:
        values.append(current_value.strip())

    # Парсим каждое значение
    return [parse_value(val) for val in values]