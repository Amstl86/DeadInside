import sys
import customtkinter as ctk

try:
    import win32event, win32api, winerror
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

from ui.main_window import MainWindow

MUTEX_NAME = "Global\\DeadInsideAppMutex"

def main():
    if HAS_PYWIN32:
        try:
            mutex = win32event.CreateMutex(None, False, MUTEX_NAME)
            if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
                print("DeadInside уже запущен.")
                sys.exit(0)
        except:
            pass
    
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("green")
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()