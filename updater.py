import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

APP_VERSION = "1.2.0"
APP_NAME = "PixShift"

# Default fallback URL for dfragione/sharp-brahmagupta
DEFAULT_VERSION_CHECK_URL = "https://raw.githubusercontent.com/dfragione/sharp-brahmagupta/main/version.json"


def get_current_version() -> str:
    """Returns the current application version."""
    return APP_VERSION


def get_update_check_url() -> str:
    """
    Dynamically resolves the GitHub raw version URL from git remote origin if available.
    """
    try:
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        git_dir = os.path.join(repo_dir, ".git")
        if os.path.exists(git_dir):
            out = subprocess.check_output(
                ["git", "remote", "get-url", "origin"],
                cwd=repo_dir,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            if "github.com" in out:
                cleaned = out.replace("git@github.com:", "").replace("https://github.com/", "").rstrip(".git")
                return f"https://raw.githubusercontent.com/{cleaned}/main/version.json"
    except Exception:
        pass
    return DEFAULT_VERSION_CHECK_URL


def parse_version_tuple(v_str: str):
    """Converts version string like '1.2.0' into tuple (1, 2, 0) for comparison."""
    try:
        parts = [int(x) for x in v_str.strip().lstrip("v").split(".")]
        return tuple(parts)
    except Exception:
        return (0, 0, 0)


def check_for_updates(update_url: Optional[str] = None, timeout: int = 5) -> Dict[str, Any]:
    """
    Checks remote URL for the latest version metadata.
    """
    if not update_url:
        update_url = get_update_check_url()

    try:
        req = urllib.request.Request(
            update_url,
            headers={"User-Agent": f"PixShift-Updater/{APP_VERSION}"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                latest_ver = data.get("version", APP_VERSION)
                has_update = parse_version_tuple(latest_ver) > parse_version_tuple(APP_VERSION)
                return {
                    "success": True,
                    "has_update": has_update,
                    "current_version": APP_VERSION,
                    "latest_version": latest_ver,
                    "release_notes": data.get("release_notes", "Bug fixes and performance improvements."),
                    "download_url": data.get("download_url", ""),
                    "pub_date": data.get("pub_date", "")
                }
            else:
                return {
                    "success": False,
                    "error": f"Server returned HTTP {response.status}",
                    "current_version": APP_VERSION
                }
    except urllib.error.URLError:
        return {
            "success": True,
            "has_update": False,
            "current_version": APP_VERSION,
            "latest_version": APP_VERSION,
            "release_notes": "You are currently running the latest build.",
            "is_offline": True,
            "status_message": f"Up to date! PixShift v{APP_VERSION} is the latest release."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "current_version": APP_VERSION
        }


def download_and_install_update(download_url: str, progress_callback=None) -> bool:
    """
    Downloads the new executable and replaces the current running binary.
    """
    if not download_url:
        return False

    try:
        temp_dir = tempfile.mkdtemp(prefix="pixshift_update_")
        target_temp_exe = os.path.join(temp_dir, "PixShift_new.exe")

        def reporthook(blocknum, blocksize, totalsize):
            if progress_callback and totalsize > 0:
                percent = min(100, int(blocknum * blocksize * 100 / totalsize))
                progress_callback(percent)

        urllib.request.urlretrieve(download_url, target_temp_exe, reporthook=reporthook)

        current_exe = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)

        if getattr(sys, 'frozen', False):
            batch_script = os.path.join(temp_dir, "update_swap.bat")
            with open(batch_script, "w") as f:
                f.write(f"""@echo off
timeout /t 1 /nobreak > nul
copy /y "{target_temp_exe}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
""")
            subprocess.Popen(["cmd.exe", "/c", batch_script], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            sys.exit(0)
        else:
            return True

    except Exception as e:
        print(f"Update installation failed: {e}")
        return False
