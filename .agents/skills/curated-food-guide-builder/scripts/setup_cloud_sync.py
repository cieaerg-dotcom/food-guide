#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Sync & LaunchAgent Setup Helper
自動設定本地美食手冊與 Google Drive / iCloud 的雙向即時同步，並註冊 macOS LaunchAgent 監控。
"""

import os
import sys
import subprocess
import argparse

PLIST_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>{SYNC_SCRIPT}</string>
    </array>
    <key>WatchPaths</key>
    <array>
{WATCH_PATHS}
    </array>
    <key>ThrottleInterval</key>
    <integer>2</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{LOG_FILE}</string>
    <key>StandardErrorPath</key>
    <string>{LOG_FILE}</string>
</dict>
</plist>
"""

def setup_sync(watch_files, label="com.foodguide.sync"):
    # 指向專案資料夾內的同步腳本與日誌目錄
    project_dir = "/Users/mac/AGY本地工作區/專案資料夾/美食景點整理"
    sync_script = os.path.join(project_dir, "scripts", "sync_food_guides.py")
    log_file = os.path.join(project_dir, "logs", "food_guides_launchd.log")
    plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")

    watch_tags = "\n".join([f"        <string>{f}</string>" for f in watch_files])
    plist_content = PLIST_TEMPLATE.format(
        LABEL=label,
        SYNC_SCRIPT=sync_script,
        WATCH_PATHS=watch_tags,
        LOG_FILE=log_file
    )

    with open(plist_path, "w", encoding="utf-8") as f:
        f.write(plist_content)

    subprocess.run(["launchctl", "unload", plist_path], stderr=subprocess.DEVNULL)
    subprocess.run(["launchctl", "load", plist_path], check=True)
    print(f"成功註冊 LaunchAgent: {plist_path}")
    print("目前監控檔案:")
    for f in watch_files:
        print(f"  - {f}")

def main():
    parser = argparse.ArgumentParser(description="設定雲端同步與監控服務")
    parser.add_argument("--files", nargs="+", required=True, help="需要監控即時同步的 HTML 檔案絕對路徑")
    args = parser.parse_args()

    setup_sync(args.files)

if __name__ == "__main__":
    main()
