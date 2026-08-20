import os
import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from app_ui import QuickJPGApp

def set_windows_app_id():
    """Ensure the taskbar shows our custom icon instead of generic Python."""
    if sys.platform == "win32":
        try:
            myappid = "quickjpg.converter.desktop.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

def main():
    # Windows high-DPI scaling configuration
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    set_windows_app_id()

    app = QApplication(sys.argv)
    app.setApplicationName("QuickJPG")
    app.setApplicationDisplayName("QuickJPG Converter")

    # Command line arguments (e.g. files dropped onto executable icon)
    initial_files = sys.argv[1:] if len(sys.argv) > 1 else None

    window = QuickJPGApp(initial_files=initial_files)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
