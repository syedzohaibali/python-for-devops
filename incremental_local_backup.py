import shutil
import datetime
import os
import platform
from pathlib import Path
from datetime import datetime as dt, timedelta

RETENTION_DAYS = 7

def _normalize_path(p: str) -> str:
    if p.startswith("/c/"):
        plat = platform.platform().lower()
        if "wsl" in plat or "microsoft" in plat: return p.replace("/c/", "/mnt/c/", 1)
        elif os.name == "nt": return "C:" + p[2:].replace("/", "\\")
    return p

def prune_old_backups(destination: str, retention_days: int = RETENTION_DAYS):
    dst = Path(destination)
    cutoff = dt.now() - timedelta(days=retention_days)
    removed = 0
    for p in dst.glob("backup_*.tar.gz*"):
        try:
            if dt.fromtimestamp(p.stat().st_mtime) < cutoff:
                p.unlink(missing_ok=True); removed += 1
        except Exception:
            pass
    if removed: print(f"Pruned {removed} old backup(s).")

def backup_files(source, destination):
    source      = _normalize_path(source)
    destination = _normalize_path(destination)
    os.makedirs(destination, exist_ok=True)

    today = datetime.date.today()
    base  = os.path.join(destination, f"backup_{today}")  # no .tar.gz here
    archive = shutil.make_archive(base, "gztar", source)
    print(f"Created: {archive}")

    prune_old_backups(destination)

source = "/c/Users/syedz/Downloads/Python-for-devops"
destination = "/c/Users/syedz/Downloads/Python-for-devops/backups"
backup_files(source, destination)
