import os
import sys
import subprocess

TASK_NAME = "DeadInsideDaily"

def add_to_startup():
    """Создаёт задачу в Планировщике Windows для запуска при входе в систему."""
    # В упакованном виде sys.executable — это путь к exe, и sys.argv[0] тоже путь к exe.
    # Для надёжности используем абсолютный путь к текущему исполняемому файлу.
    app_path = os.path.abspath(sys.argv[0])
    cmd = f'schtasks /Create /SC ONLOGON /TN "{TASK_NAME}" /TR "{app_path}" /F'
    subprocess.run(cmd, shell=True)

def remove_from_startup():
    """Удаляет задачу из автозагрузки."""
    cmd = f'schtasks /Delete /TN "{TASK_NAME}" /F'
    subprocess.run(cmd, shell=True)

def is_in_startup():
    """Проверяет, существует ли задача в планировщике."""
    result = subprocess.run(f'schtasks /Query /TN "{TASK_NAME}"', 
                            shell=True, capture_output=True, text=True)
    return result.returncode == 0