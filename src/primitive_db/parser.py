# src/primitive_db/parser.py

def parse_where_clause(where_condition):
    if not where_condition:
        return None

    condition = where_condition.strip()

    if "=" not in condition:
        raise ValueError("Некорректный формат условия WHERE. Используйте: "
                            "столбец = значение")

    parts = condition.split("=", 1)
    column = parts[0].strip()
    value_str = parts[1].strip()

    value = parse_value(value_str)

    return {column: value}


def parse_set_clause(set_condition):
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
    if (value_str.startswith('"') and value_str.endswith('"')) or \
            (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    if value_str.lower() == "true":
        return True
    elif value_str.lower() == "false":
        return False

    try:
        return int(value_str)
    except ValueError:
        try:
            return float(value_str)
        except ValueError:
            pass

    return value_str


def parse_values(values_str):
    values_str = values_str.strip()
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1]

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

    return [parse_value(val) for val in values]