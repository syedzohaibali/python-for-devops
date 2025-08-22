import shutil
import datetime
import os
import platform

def _normalize_path(p: str) -> str:
    # If user wrote /c/..., convert based on environment
    if p.startswith("/c/"):
        plat = platform.platform().lower()
        if "wsl" in plat or "microsoft" in plat:       # WSL
            return p.replace("/c/", "/mnt/c/", 1)
        elif os.name == "nt":                           # Windows
            return "C:" + p[2:].replace("/", "\\")
    return p

def backup_files(source, destination):
    # normalize both paths
    source = _normalize_path(source)
    destination = _normalize_path(destination)

    # ensure destination exists
    os.makedirs(destination, exist_ok=True)

    today = datetime.date.today()
    backup_file_name = os.path.join(destination, f"backup_{today}.tar.gz")

    # make_archive expects base name without extension when using 'gztar'
    shutil.make_archive(backup_file_name.replace(".tar.gz", ""), "gztar", source)
    print(f"Created: {backup_file_name}")

source = "/c/Users/syedz/Downloads/Python-for-devops"
destination = "/c/Users/syedz/Downloads/Python-for-devops/backups"
backup_files(source, destination)
