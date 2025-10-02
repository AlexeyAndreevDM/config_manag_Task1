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