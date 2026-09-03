import os
import shutil
import subprocess
import sys


def run_nuitka_build():
    entry_point = "pdf_reader.py"

    if not os.path.exists(entry_point):
        print(f"[ERROR] Could not find {entry_point} in root directory!")
        sys.exit(1)

    # Locate UPX directory and add it to system PATH environment for this process
    upx_dir = os.path.join(os.path.dirname(__file__), "upx-5.2.1-win64")
    if os.path.exists(os.path.join(upx_dir, "upx.exe")):
        os.environ["PATH"] = upx_dir + os.pathsep + os.environ["PATH"]
        print(f"[INFO] Added UPX to PATH from: {upx_dir}")
    elif shutil.which("upx"):
        print("[INFO] UPX detected in system PATH.")
    else:
        print("[WARNING] UPX not found. Binary will not be compressed.")

    command = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--onefile",
        "--remove-output",
        "--assume-yes-for-downloads",
        "--windows-console-mode=disable",
    ]

    # Include app icon if available
    if os.path.exists("app_icon.ico"):
        command.append("--windows-icon-from-ico=app_icon.ico")

    # Exclude unused heavy libraries
    unwanted_modules = [
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "PIL",
        "unittest",
        "pydoc",
    ]
    for module in unwanted_modules:
        command.append(f"--nofollow-import-to={module}")

    command.append(entry_point)

    print(f"[INFO] Compiling {entry_point} with Nuitka...")
    subprocess.run(command, check=True)


if __name__ == "__main__":
    run_nuitka_build()