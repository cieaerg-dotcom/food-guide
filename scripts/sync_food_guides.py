#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動同步美食避雷隨身手冊至 Google Drive 與 iCloud Drive
比對 SHA256 雜湊值，若有變更則同步更新。
"""

import os
import sys
import shutil
import hashlib
from datetime import datetime

PROJECT_DIR = "/Users/mac/AGY本地工作區/專案資料夾/美食景點整理"
SOURCE_FILE = os.path.join(PROJECT_DIR, "美食避雷隨身手冊.html")

TARGET_GD = os.path.expanduser("~/Library/CloudStorage/GoogleDrive-cieaer.g@gmail.com/我的雲端硬碟/AGY工作區GD/美食隨身手冊")
TARGET_ICLOUD = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/AGY工作區i/美食隨身手冊")

def get_sha256(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def log(msg: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def sync():
    if not os.path.exists(SOURCE_FILE):
        log(f"來源手冊不存在: {SOURCE_FILE}")
        return

    src_hash = get_sha256(SOURCE_FILE)
    fname = os.path.basename(SOURCE_FILE)

    targets = [
        ("Google Drive", TARGET_GD),
        ("iCloud Drive", TARGET_ICLOUD)
    ]

    for name, tdir in targets:
        os.makedirs(tdir, exist_ok=True)
        dest_path = os.path.join(tdir, fname)
        dest_hash = get_sha256(dest_path)

        if src_hash != dest_hash:
            shutil.copy2(SOURCE_FILE, dest_path)
            log(f"已同步至 {name}: {dest_path}")
        else:
            log(f"{name} 檔案內容已為最新 (SHA256 相符)")

if __name__ == "__main__":
    sync()
