import shutil
import datetime
import os
import platform

# NEW
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# --- S3 settings (edit) ---
S3_BUCKET = "testing11669"
S3_PREFIX = "server1/"   # becomes s3://bucket/server1/<file>
# --------------------------

def _normalize_path(p: str) -> str:
    # If user wrote /c/..., convert based on environment
    if p.startswith("/c/"):
        plat = platform.platform().lower()
        if "wsl" in plat or "microsoft" in plat:       # WSL
            return p.replace("/c/", "/mnt/c/", 1)
        elif os.name == "nt":                           # Windows
            return "C:" + p[2:].replace("/", "\\")
    return p

# NEW
def upload_to_s3(local_path: str):
    s3 = boto3.client("s3")
    key = f"{S3_PREFIX}{os.path.basename(local_path)}" if S3_PREFIX else os.path.basename(local_path)
    s3.upload_file(local_path, S3_BUCKET, key)
    print(f"Uploaded to s3://{S3_BUCKET}/{key}")

def backup_files(source, destination):
    # normalize both paths
    source = _normalize_path(source)
    destination = _normalize_path(destination)

    # ensure destination exists
    os.makedirs(destination, exist_ok=True)

    # NEW: timestamp so repeated runs don't overwrite
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file_name = os.path.join(destination, f"backup_{ts}.tar.gz")

    # make_archive expects base name without extension when using 'gztar'
    archive_path = shutil.make_archive(backup_file_name.replace(".tar.gz", ""), "gztar", source)
    print(f"Created: {archive_path}")

    # NEW: upload
    try:
        upload_to_s3(archive_path)
    except (BotoCoreError, ClientError) as e:
        print(f"S3 upload failed: {e}")

source = "/c/Users/syedz/Downloads/Python-for-devops"
destination = "/c/Users/syedz/Downloads/Python-for-devops/backups"
backup_files(source, destination)
# This script creates a backup of files and uploads it to an S3 bucket.