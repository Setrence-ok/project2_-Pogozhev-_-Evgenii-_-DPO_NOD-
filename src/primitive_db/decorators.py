# src/deco.py

import functools
import time


def handle_db_errors(func):
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


def confirm_action(action_name, return_):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = input(f'Вы уверены, что хотите выполнить "{action_name}"? '
                             f'[y/n]: ')
            if response.lower() != 'y':
                print("Операция отменена.")
                return return_

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        try:
            result = func(*args, **kwargs)
            end_time = time.monotonic()
            execution_time = end_time - start_time
            print(f'Функция "{func.__name__}" выполнилась за '
                  f'{execution_time:.6f} секунд')
        except Exception:
            end_time = time.monotonic()
            execution_time = end_time - start_time
            print(f'Функция "{func.__name__}" выполнилась за '
                  f'{execution_time:.6f} секунд')
            return
        return result

    return wrapper


def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        else:
            result = value_func()
            cache[key] = result
            return result

    return cache_result
