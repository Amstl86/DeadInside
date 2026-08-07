import os
import sys
import subprocess

def add_to_startup():
    """Создаёт задачу в Планировщике Windows для запуска при входе в систему."""
    python_exe = sys.executable
    script_path = os.path.abspath(sys.argv[0])
    task_name = "GoalTrackerDaily"
    cmd = f'schtasks /Create /SC ONLOGON /TN "{task_name}" /TR "{python_exe} {script_path}" /F'
    subprocess.run(cmd, shell=True)

def remove_from_startup():
    task_name = "GoalTrackerDaily"
    cmd = f'schtasks /Delete /TN "{task_name}" /F'
    subprocess.run(cmd, shell=True)