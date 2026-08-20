import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    print("========================================")
    print("  Building QuickJPG Standalone .EXE     ")
    print("========================================")
    
    icon_path = os.path.abspath("assets/icon.ico")
    if not os.path.exists(icon_path):
        from generate_icon import generate_app_icon
        generate_app_icon()

    # PyInstaller arguments
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",             # Build onedir for fast startup and portable folder, then we can also do onefile
        "--windowed",           # No console window
        "--name", "QuickJPG",
        f"--icon={icon_path}",
        f"--add-data=assets{os.pathsep}assets",
        "--hidden-import", "PyQt6.QtSvg",
        "--hidden-import", "pillow_heif",
        "--hidden-import", "send2trash",
        "--clean",
        "main.py"
    ]

    print(f"Running PyInstaller: {' '.join(pyinstaller_args)}")
    result = subprocess.run(pyinstaller_args)

    if result.returncode != 0:
        print("PyInstaller build failed!")
        sys.exit(1)

    print("\nAlso creating single-file portable executable (QuickJPG-Portable.exe)...")
    portable_args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "QuickJPG",
        f"--icon={icon_path}",
        f"--add-data=assets{os.pathsep}assets",
        "--hidden-import", "PyQt6.QtSvg",
        "--hidden-import", "pillow_heif",
        "--hidden-import", "send2trash",
        "main.py"
    ]
    subprocess.run(portable_args)

    exe_path = os.path.abspath("dist/QuickJPG.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("========================================")
        print(" BUILD SUCCESSFUL! ")
        print(f" Output: {exe_path} ({size_mb:.1f} MB)")
        print("========================================")
    else:
        print("Warning: QuickJPG.exe was not found in dist/")

if __name__ == "__main__":
    build_executable()
