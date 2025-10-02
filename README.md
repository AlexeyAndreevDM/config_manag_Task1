# Эмулятор командной строки - Этап 3-4

## Общее описание
Проект представляет собой эмулятор командной строки UNIX-подобных операционных систем, реализованный на Python. На третьем и четвертом этапах разработки добавлена поддержка виртуальной файловой системы (VFS) и основных UNIX-команд.

## Функции и настройки

### Основные возможности:
- **Интерактивный интерфейс**: Консольный интерфейс с приглашением к вводу
- **Парсер команд**: Корректная обработка аргументов в кавычках с использованием shlex
- **Обработка ошибок**: Сообщения об ошибках для неизвестных команд и проблем со скриптами
- **Виртуальная файловая система**: Поддержка VFS на основе ZIP-архивов в формате base64
- **Полноценные команды**: Реализованы команды ls, cd, cal, whoami, who и exit

### Параметры командной строки:
- **--vfs-path** [ПУТЬ] - физический путь к ZIP-архиву, представляющему виртуальную файловую систему
- **--script** [ПУТЬ] - путь к стартовому скрипту для выполнения (опционально)

### Формат приглашения:
Приглашение к вводу отображается в формате: имя_vfs:текущий_путь$

### Реализованные команды:

#### Команды файловой системы:
- **ls [путь]** - вывод содержимого директории в VFS
- **cd [путь]** - изменение текущей директории в VFS

#### Системные команды:
- **cal [месяц] [год]** - вывод календаря (текущего месяца/года или указанного)
- **whoami** - вывод имени текущего пользователя
- **who** - вывод информации о текущем пользователе и системе
- **exit** - завершение работы эмулятора

### Особенности обработки:
- VFS загружается из ZIP-архива, закодированного в base64
- Поддерживаются абсолютные пути в VFS
- Автоматическая обработка относительных путей относительно текущей директории
- Корректная обработка ошибок загрузки VFS (файл не найден, неверный формат)
- Отладочная информация выводится в stderr

## Виртуальная файловая система (VFS)

### Особенности реализации:
- Все операции производятся в памяти без распаковки данных
- Источником VFS является ZIP-архив в формате base64
- Поддерживается древовидная структура файлов и папок
- Обработка ошибок (файл/директория с одинаковыми именами)

### Формат VFS:
ZIP-архив должен содержать обычную файловую структуру. При загрузке архива:
- Файлы сохраняются с их содержимым
- Директории создаются как узлы в дереве VFS

## Сборка и запуск

### Базовый запуск:
```bash
python task1.py
```

### Запуск с VFS:
```bash
# С указанием пути к ZIP-архиву VFS
python task1.py --vfs-path vfs_name.zip
```

### Запуск со скриптом:
```bash
# Со стартовым скриптом
python task1.py --script test_script.txt

# Со всеми параметрами
python task1.py --vfs-path vfs_name.zip --script test_name.txt
```

## Структура VFS для тестирования

Реализованные тестовые VFS:
1. **Минимальная VFS** - пустой архив или с одним файлом
2. **VFS с несколькими фалами** - несколько файлов в разных директориях
3. **Глубокая структура** - не менее 3 уровней вложенности директорий

## Тестирование

### Тестовые скрипты:

#### Базовое тестирование (normal_test.txt):
```bash
who
ls
cd 3_level_VFS/lvl2
ls
cal
cd ..
ls
whoami
cal 12 2025
```

#### Несколько тестовых файлов могут быть запущены скриптом run_file.py:
```bash
import subprocess

# Тест 1: Нормальный сценарий
print("Тест 1: normal_test.txt")
subprocess.run(["python", "task1.py", "--vfs-path", "3_level_VFS.zip", "--script", "normal_test.txt"])

# Тест 2: Обработка ошибок  
print("\nТест 2: error_test.txt")
subprocess.run(["python", "task1.py", "--vfs-path", "min_VFS.zip", "--script", "error_test.txt"])

# Тест 3: Команда exit в скрипте
print("\nТест 3: exit_test.txt")
subprocess.run(["python", "task1.py", "--vfs-path", "few_Files_VFS.zip", "--script", "exit_test.txt"])
```

#### Тестирование ошибок (error_test.txt):
```bash
ls /nonexistent
unknown_command
cd /invalid/path
cal invalid
cal 13 2024
cal 1 10000
```

#### Тестирование выхода (exit_test.txt):
```bash
ls
exit
echo "??? ?????? ?? ?????? ???????????"
```

### Примеры использования:

```bash
# Тестирование с различными VFS
python task1.py --vfs-path min_VFS.zip --script normal_test.txt
python task1.py --vfs-path few_Files_VFS.zip --script normal_test.txt
python task1.py --vfs-path 3_level_VFS.zip --script normal_test.txt

# Демонстрация обработки ошибок
python task1.py --vfs-path few_Files_VFS.zip --script error_test.txt
python task1.py --vfs-path invalid.zip --script normal_test.txt
python task1.py --script nonexistent.txt
```

## Примеры использования
<img width="994" height="416" alt="image" src="https://github.com/user-attachments/assets/f34561e7-def4-4d1b-b3ca-0ba4772352e2" />
<img width="651" height="171" alt="Screenshot 2025-09-22 at 10 53 04" src="https://github.com/user-attachments/assets/18be39d2-4b89-4a06-b1fd-7a5c21ebb2f0" />
<img width="650" height="100" alt="Screenshot 2025-09-22 at 10 55 50" src="https://github.com/user-attachments/assets/1ef92ce2-77a3-47c8-a112-f0da1f9fecee" />
<img width="658" height="173" alt="Screenshot 2025-09-22 at 10 56 26" src="https://github.com/user-attachments/assets/480c8ac6-4965-4902-9ed4-abba0cc0eae1" />
<img width="640" height="402" alt="Screenshot 2025-09-22 at 16 15 44" src="https://github.com/user-attachments/assets/9ff13a17-d350-4173-85c3-78d4f47d42db" />


