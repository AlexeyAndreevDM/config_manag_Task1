import os
import platform
import shlex
import argparse
import sys
import zipfile
import base64
from io import BytesIO
import calendar
import datetime
import getpass
import pwd

class VFS:
    def __init__(self, base64_zip_data):
        self.fs_tree = {}
        self.root_path = "/"
        try:
            zip_bytes = base64.b64decode(base64_zip_data)
        except Exception as e:
            raise ValueError(f"Ошибка декодирования base64: {e}")

        try:
            with zipfile.ZipFile(BytesIO(zip_bytes), 'r') as zip_file:
                for file_info in zip_file.infolist():
                    path = file_info.filename
                    # Убираем начальный и конечный слэши, разбиваем путь
                    parts = [p for p in path.strip('/').split('/') if p]
                    
                    if not parts: # Это корень? 
                        continue # Не пытаемся обработать корневую директорию как файл или папку

                    current_level = self.fs_tree
                    # Проходим по директориям в пути
                    for part in parts[:-1]:
                        if part not in current_level:
                            current_level[part] = {'__type__': 'directory', '__children__': {}}
                        current_level = current_level[part]['__children__']

                    # Добавляем файл или пустую директорию
                    if file_info.is_dir():
                        current_level[parts[-1]] = {'__type__': 'directory', '__children__': {}}
                    else: # Это файл
                        current_level[parts[-1]] = {'__type__': 'file', '__data__': zip_file.read(file_info.filename)}
                    
        except zipfile.BadZipFile:
            raise ValueError("Файл не является корректным ZIP-архивом.")
        except Exception as e:
            raise ValueError(f"Ошибка при разборе ZIP-архива: {e}")

    def _navigate_to_path(self, path_str, create_dirs=False):
        if not path_str.startswith('/'):
            raise ValueError("Поддерживаются только абсолютные пути.")

        parts = [p for p in path_str.strip('/').split('/') if p]

        # Обработка корневого пути "/"
        if not parts:
            return self.fs_tree, None, True

        current_level = self.fs_tree
        last_part = ""

        # Навигация до предпоследнего элемента
        for part in parts[:-1]:
            if part not in current_level:
                # Если create_dirs=True и директория не существует, создаем её
                if create_dirs:
                    current_level[part] = {'__type__': 'directory', '__children__': {}}
                else:
                    return None, part, False
            node = current_level[part]
            # Проверяем, является ли узел директорией (иначе путь неверен)
            if node['__type__'] != 'directory':
                return None, part, False
            current_level = node['__children__']
            last_part = part

        # Обработка последнего элемента пути
        target_key = parts[-1]
        exists = target_key in current_level
        return current_level, target_key, exists

    def list_dir(self, path_str):
        parent, key, exists = self._navigate_to_path(path_str)
        if not exists:
            return None
        
        # Если путь к корню, key будет None
        if key is None:
            # parent - это fs_tree, список его ключей - содержимое корня
            return list(parent.keys())
        
        node = parent[key]
        if node['__type__'] != 'directory':
            return None
        return list(node['__children__'].keys())

    def change_dir(self, path_str):
        # Требуется абсолютный путь
        if path_str == "/":
            return True # Всегда можно перейти в корень
        parent, key, exists = self._navigate_to_path(path_str)
        if not exists:
            return False
        node = parent[key]
        return node['__type__'] == 'directory'

    def get_file_content(self, path_str):
        parent, key, exists = self._navigate_to_path(path_str)
        if not exists:
            return None
        
        # Если путь к корню, это не файл
        if key is None:
            return None
            
        node = parent[key]
        if node['__type__'] != 'file':
            return None
        return node.get('__data__', b'')


class Shell:
    # Класс эмулятора с основными командами
    def __init__(self, vfs_instance):
        self.vfs = vfs_instance
        self.current_path = "/" # Текущая директория в VFS

    def ls(self, args):
        path = args[0] if args else self.current_path
        if not path.startswith('/'):
            # Если путь относительный, делаем его абсолютным относительно текущего
            path = os.path.normpath(os.path.join(self.current_path, path)).replace('\\', '/')
            if not path.startswith('/'):
                 path = '/' + path

        items = self.vfs.list_dir(path)
        if items is None:
            return f"ls: cannot access '{path}': No such file or directory"
        return "\n".join(items)

    def cd(self, args):
        if not args:
            path = "/"
        else:
            path = args[0]
        
        if not path.startswith('/'):
            # Если путь относительный, делаем его абсолютным относительно текущего
            new_path = os.path.normpath(os.path.join(self.current_path, path)).replace('\\', '/')
            if not new_path.startswith('/'):
                 new_path = '/' + new_path
        else:
            new_path = path

        if self.vfs.change_dir(new_path):
            self.current_path = new_path
            return "" # Команда cd не выводит ничего в случае успеха
        else:
            return f"cd: {path}: No such file or directory"

    def cal(self, args):
        # Команда cal - выводит календарь
        # Если аргументы есть, пытаемся их распарсить как год/месяц
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month

        if len(args) == 1:
            try:
                month = int(args[0])
                if 1 <= month <= 12:
                    pass # Месяц указан, год остается текущий
                else:
                    return f"cal: invalid month: {month}"
            except ValueError:
                try:
                    year = int(args[0])
                    if 1 <= year <= 9999:
                        month = None # Показать весь год
                    else:
                        return f"cal: invalid year: {year}"
                except ValueError:
                    return f"cal: invalid argument: {args[0]}"
        elif len(args) == 2:
            try:
                month = int(args[0])
                year = int(args[1])
                if not (1 <= month <= 12):
                    return f"cal: invalid month: {month}"
                if not (1 <= year <= 9999):
                    return f"cal: invalid year: {year}"
            except ValueError:
                return f"cal: invalid arguments: {args[0]} {args[1]}"
        elif len(args) > 2:
            return f"cal: too many arguments"

        if month is None:
            # Показать календарь на весь год
            return calendar.TextCalendar().formatyear(year)
        else:
            # Показать календарь на месяц
            return calendar.month(year, month).rstrip() # .rstrip() убирает лишние символы новой строки в конце

    def whoami(self, args):
        # Команда whoami - выводит имя текущего пользователя
        try:
            return getpass.getuser()
        except Exception:
            return "unknown" # Если не удалось определить пользователя

    def who(self, args):
        current_user = self.whoami([])
        # Используем platform.node() как имя хоста
        hostname = platform.node()
        # Используем текущее время
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        # Формат строки как у стандартной команды who: пользователь терминал дата_время хост
        # В эмуляторе терминал и хост фиктивные
        terminal = "console" # или "pts/0" для эмуляции
        # Для простоты эмулируем только текущего пользователя
        return f"{current_user}  {terminal}  {current_time}  {hostname}"

    @staticmethod
    def unknown(command):
        return f"{command}: command not found" # Для неизвестной команды

    def parser(self, input_string):
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
            return self.ls(args), False
        elif command == "cd":
            return self.cd(args), False
        elif command == "cal":
            return self.cal(args), False
        elif command == "whoami":
            return self.whoami(args), False
        elif command == "who":
            return self.who(args), False
        elif command == "exit":
            return "", True  # Устанавливаем флаг выхода
        else:
            return Shell.unknown(command), False


# Создаем парсер аргументов командной строки
parser = argparse.ArgumentParser(description='Эмулятор командной оболочки UNIX-подобной ОС')
parser.add_argument('--vfs-path', type=str, default=None,
                   help='Путь к ZIP-архиву, представляющему VFS')
parser.add_argument('--script', type=str,
                   help='Путь к стартовому скрипту для выполнения')

# Парсим аргументы командной строки
args = parser.parse_args()

vfs_instance = None
if args.vfs_path:
    try:
        # Читаем ZIP-файл и кодируем его в base64 для передачи в VFS
        with open(args.vfs_path, 'rb') as f:
            zip_data = f.read()
        base64_zip_string = base64.b64encode(zip_data).decode('utf-8')
        vfs_instance = VFS(base64_zip_string)
        print(f"Debug: VFS loaded from {args.vfs_path}", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: VFS file '{args.vfs_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except ValueError as ve:
        print(f"Error: Invalid VFS format - {ve}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading VFS: {str(e)}", file=sys.stderr)
        sys.exit(1)
else:
    # Если --vfs-path не указан, создаем пустую VFS для демонстрации
    print("Предупреждение: Путь к VFS не был указан, запущен интерактивный режим", file=sys.stderr)
    # Создаем пустой ZIP в памяти и кодируем его
    empty_zip_buffer = BytesIO()
    with zipfile.ZipFile(empty_zip_buffer, 'w') as zf:
        pass # Создаем пустой архив
    empty_zip_data = empty_zip_buffer.getvalue()
    base64_empty_zip_string = base64.b64encode(empty_zip_data).decode('utf-8')
    vfs_instance = VFS(base64_empty_zip_string)


# Создаем экземпляр оболочки с VFS
shell = Shell(vfs_instance)

# Отладочный вывод параметров в поток вывода для ошибок
print(f"Debug: VFS initialized", file=sys.stderr)
if args.script:
    print(f"Debug: Startup script = {args.script}", file=sys.stderr)

# Настройка приглашения командной строки
vfs_name = "vfs_root" # Имя можно брать из аргументов или из VFS, если есть мета-информация
hostname = platform.node()
invite = lambda: f"{vfs_name}:{shell.current_path}$ " # lambda для динамического обновления пути

# Выполнение стартового скрипта, если он указан
if args.script:
    try:
        with open(args.script, 'r') as f:
            # Читаем и выполняем команды из скрипта построчно
            for line in f:
                line = line.strip()
                # # Пропускаем пустые строки и комментарии - не нужно было
                # if not line or line.startswith('#'):
                #     continue
                
                # Эмулируем ввод пользователя
                print(f"{invite()}{line}")
                # Выполняем команду и получаем результат
                result, should_exit = shell.parser(line)
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
        s = input(invite())
    except (EOFError, KeyboardInterrupt):
        # Обработка Ctrl+D и Ctrl+C
        print()
        break
        
    # Обработка команды
    result, should_exit = shell.parser(s)
    # Вывод результата, если он есть
    if result:
        print(result)
    # Выход при команде exit
    if should_exit:
        break