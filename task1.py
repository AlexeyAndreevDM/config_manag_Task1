import os
import platform
import shlex
import argparse
import sys

class Shell:
    # Класс эмулятора оболочки с основными командами
    
    @staticmethod
    def ls(args):
        # Заглушка для команды ls - выводит имя команды и аргументы
        return f"ls: {', '.join(args)}"
    
    @staticmethod
    def cd(args):
        # Заглушка для команды cd - выводит имя команды и аргументы
        return f"cd: {', '.join(args)}"

    @staticmethod
    def unknown(command):
        return f"{command}: command not found" # Для неизвестной команды

    @staticmethod
    def parser(input_string):
        # Парсер введенной строки
        try:
            # Используем shlex для корректного разбиения строки с кавычками
            parts = shlex.split(input_string)
        except ValueError as e:
            return f"Syntax error: {str(e)}", False
            
        # Пропускаем пустые строки
        if not parts:
            return "", False
            
        command = parts[0] # выделяем в строке саму команду
        args = parts[1:] if len(parts) > 1 else [] # выделяем аргументы
        
        # Обработка известных команд
        if command == "ls":
            return Shell.ls(args), False
        elif command == "cd":
            return Shell.cd(args), False
        elif command == "exit":
            return "", True  # Устанавливаем флаг выхода
        else:
            return Shell.unknown(command), False

# Создаем парсер аргументов командной строки
parser = argparse.ArgumentParser(description='Эмулятор командной оболочки UNIX-подобной ОС')
parser.add_argument('--vfs-path', type=str, default=os.getcwd(),
                   help='Физический путь к виртуальной файловой системе')
parser.add_argument('--script', type=str,
                   help='Путь к стартовому скрипту для выполнения')

# Парсим аргументы командной строки
args = parser.parse_args()

# Отладочный вывод параметров в поток вывода для ошибок
print(f"Debug: VFS path = {args.vfs_path}", file=sys.stderr)
if args.script:
    print(f"Debug: Startup script = {args.script}", file=sys.stderr)

# Настройка приглашения командной строки
vfs_name = "my_vfs"
hostname = platform.node()
invite = f"{vfs_name} $ "

# Выполнение стартового скрипта, если он указан
if args.script:
    try:
        with open(args.script, 'r') as f:
            # Читаем и выполняем команды из скрипта построчно
            for line in f:
                line = line.strip()
                # Пропускаем пустые строки и комментарии
                if not line:
                    continue
                
                # Эмулируем ввод пользователя
                print(f"{invite}{line}")
                # Выполняем команду и получаем результат
                result, should_exit = Shell.parser(line)
                if result:
                    print(result)
                # Если команда exit, прерываем выполнение скрипта
                if should_exit:
                    sys.exit(0)
                    
    except FileNotFoundError:
        # Если файл скрипта не найден, выводим ошибку
        print(f"Error: Script file '{args.script}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # При других ошибках скрипта выводим сообщение
        print(f"Error executing script: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # После успешного выполнения скрипта завершаем программу
    sys.exit(0)

# Основной цикл (только если скрипт не указан)
while True:
    try:
        # Чтение команды от пользователя
        s = input(invite)
    except (EOFError, KeyboardInterrupt):
        # Обработка Ctrl+D и Ctrl+C
        print()
        break
        
    # Обработка команды
    result, should_exit = Shell.parser(s)
    # Вывод результата, если он есть
    if result:
        print(result)
    # Выход при команде exit
    if should_exit:
        break