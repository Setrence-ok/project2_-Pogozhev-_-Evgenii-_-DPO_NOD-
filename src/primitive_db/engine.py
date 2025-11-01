# src/primitive_db/engine.py
import prompt


def welcome():
    print("Первая попытка запустить проект!\n")
    print("***")

    while True:
        command = prompt.string("Введите команду: ")  # Используем ask вместо prompt
        if command == "exit":
            print("Выход из программы.")
            break
        elif command == "help":
            print("\n<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print("Неизвестная команда. Введите 'help' для получения списка команд.")
