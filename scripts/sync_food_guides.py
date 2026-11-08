#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive & iCloud 雙雲端增量同步腳本
監控專案資料夾（/Users/mac/AGY本地工作區/專案資料夾/美食景點整理）內之美食手冊檔案，
並於檔案更新時自動同步至 Google Drive、iCloud Drive 與專案內 guides/ 備份目錄。
"""

import os
import shutil
import hashlib
from datetime import datetime

# 專案標準根目錄路徑
PROJECT_DIR = "/Users/mac/AGY本地工作區/專案資料夾/美食景點整理"
GUIDES_BACKUP_DIR = os.path.join(PROJECT_DIR, "guides")

LOG_DIR = os.path.join(PROJECT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "food_guides_sync.log")

# 雲端同步目標路徑（Google Drive 與 Apple iCloud Drive）
TARGETS = [
    os.path.expanduser("~/Library/CloudStorage/GoogleDrive-cieaer.g@gmail.com/我的雲端硬碟/AGY工作區GD/美食隨身手冊"),
    os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/AGY工作區i/美食隨身手冊")
]

# 納入同步的單一整合版手冊檔案清單
FILES = [
    "美食避雷隨身手冊.html"
]

# 已淘汰之舊版分散檔案清單（同步時自動從雲端與備份目錄清理）
LEGACY_FILES = [
    "新營美食避雷隨身手冊.html",
    "嘉義美食精選隨身手冊.html",
    "index.html"
]

def get_hash(filepath: str) -> str | None:
    """計算檔案之 SHA-256 雜湊值，若檔案不存在則回傳 None。"""
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def log(msg: str) -> None:
    """將同步訊息加上時間戳記輸出至終端機並寫入日誌檔。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{now}] {msg}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def sync() -> None:
    """比對專案目錄內的手冊檔案雜湊值，將變更增量同步至雙雲端與 guides 備份目錄。"""
    updated_count = 0
    os.makedirs(GUIDES_BACKUP_DIR, exist_ok=True)

    for target_dir in TARGETS:
        try:
            os.makedirs(target_dir, exist_ok=True)
            for fname in FILES:
                src_path = os.path.join(PROJECT_DIR, fname)
                if not os.path.exists(src_path):
                    continue

                dst_path = os.path.join(target_dir, fname)
                src_hash = get_hash(src_path)
                dst_hash = get_hash(dst_path)

                if src_hash != dst_hash:
                    shutil.copy2(src_path, dst_path)
                    target_name = "GoogleDrive" if "GoogleDrive" in target_dir else "iCloud"
                    log(f"已同步 [{fname}] 至 {target_name}")
                    updated_count += 1

            # 自動移除雲端上已整合淘汰之舊版分散檔案
            for old_name in LEGACY_FILES:
                old_dst = os.path.join(target_dir, old_name)
                if os.path.exists(old_dst):
                    os.remove(old_dst)
                    target_name = "GoogleDrive" if "GoogleDrive" in target_dir else "iCloud"
                    log(f"已清理 {target_name} 舊版分散檔案 [{old_name}]")
                    updated_count += 1
        except Exception as e:
            log(f"同步至 {target_dir} 時發生錯誤: {e}")

    # 同步備份至專案內 guides/ 子目錄並清理舊檔
    for fname in FILES:
        src_path = os.path.join(PROJECT_DIR, fname)
        backup_path = os.path.join(GUIDES_BACKUP_DIR, fname)
        if os.path.exists(src_path) and get_hash(src_path) != get_hash(backup_path):
            shutil.copy2(src_path, backup_path)
    for old_name in LEGACY_FILES:
        old_backup = os.path.join(GUIDES_BACKUP_DIR, old_name)
        if os.path.exists(old_backup):
            os.remove(old_backup)

    if updated_count == 0:
        log("檢查完成：雲端檔案皆為最新版本，無需更新。")

if __name__ == "__main__":
    sync()
