# src/deco.py

import time
import functools


def handle_db_errors(func):
    """
    Декоратор для обработки ошибок базы данных
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец '{e}' не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except FileNotFoundError:
            print("Ошибка: Файл не найден. Возможно, база данных не инициализирована.")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    return wrapper


def confirm_action(action_name):
    """
    Декоратор для подтверждения опасных операций
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if response.lower() != 'y':
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """
    Декоратор для замера времени выполнения функции
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f'Функция "{func._name_}" выполнилась за {execution_time:.3f} секунд')
        return result

    return wrapper


def create_cacher():
    """
    Фабрика функций для кэширования
    """
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        else:
            result = value_func()
            cache[key] = result
            return result

    return cache_result