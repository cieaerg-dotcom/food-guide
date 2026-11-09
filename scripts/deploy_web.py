#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本機與 GitHub Pages 網頁同步腳本 (deploy_web.py)
功能：
1. 執行 build_unified_guide.py 重新產生最新版單檔 HTML 與 web_dist/ (PWA 網站包)。
2. 檢查 Git 變更，若有更新則自動 commit 並 push 至 GitHub。
3. 觸發 GitHub Actions，自動同步更新線上 GitHub Pages 網站。
"""

import os
import sys
import subprocess
from datetime import datetime

PROJECT_DIR = "/Users/mac/AGY本地工作區/專案資料夾/美食景點整理"
BUILD_FOOD_SCRIPT = os.path.join(PROJECT_DIR, "scripts", "build_unified_guide.py")
BUILD_ATTRACTIONS_SCRIPT = os.path.join(PROJECT_DIR, "scripts", "build_attractions_guide.py")
BUILD_SEAVIEW_SCRIPT = os.path.join(PROJECT_DIR, "scripts", "build_seaview_guide.py")

def log(msg: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def run_cmd(cmd: list, cwd: str = PROJECT_DIR) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

def main():
    log("開始執行本機手冊與網頁同步流程（純本地產出 + GitHub Pages 部署，已全面停用雲端硬碟同步）...")

    # 1. 重新建置最新手冊（美食避雷、美拍景點、看海旅宿）
    targets = [
        ("美食避雷手冊", BUILD_FOOD_SCRIPT),
        ("美拍私房景點手冊", BUILD_ATTRACTIONS_SCRIPT),
        ("看海放空旅宿手冊", BUILD_SEAVIEW_SCRIPT)
    ]
    for name, script in targets:
        if os.path.exists(script):
            res = run_cmd([sys.executable, script])
            if res.returncode != 0:
                log(f"{name} 建置失敗: {res.stderr}")
                sys.exit(1)
            print(res.stdout.strip())
        else:
            log(f"找不到建置腳本: {script}")
            sys.exit(1)

    # 2. 檢查 Git 是否有設定 remote
    res_remote = run_cmd(["git", "remote", "-v"])
    has_remote = bool(res_remote.stdout.strip())

    # 3. 檢查是否有檔案變更需要提交
    res_status = run_cmd(["git", "status", "--porcelain"])
    changes = res_status.stdout.strip()

    if changes:
        log("偵測到本機檔案變更，進行 Git commit...")
        run_cmd(["git", "add", "."])
        commit_msg = f"update: 更新手冊內容與網頁包 ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        res_commit = run_cmd(["git", "commit", "-m", commit_msg])
        if res_commit.returncode == 0:
            log("已完成本機 Git 提交。")
        else:
            log(f"Git commit 提示: {res_commit.stderr.strip() or res_commit.stdout.strip()}")
    else:
        log("本機檔案皆為最新，無須建立新 commit。")

    # 4. 若已綁定 GitHub Remote，則推送並同步至線上網頁
    if has_remote:
        log("正在推送至 GitHub，觸發 GitHub Pages 網站發布...")
        res_push = run_cmd(["git", "push"])
        if res_push.returncode == 0:
            log("✅ 推送成功！GitHub Pages 將在 1~2 分鐘內自動完成網頁更新。")
        else:
            log(f"⚠️ Git 推送未完成 (可能尚未設定 upstream 或遠端分支):\n{res_push.stderr.strip()}")
            log("提示：首次推送請執行：git push -u origin main")
    else:
        log("ℹ️ 尚未綁定 GitHub 儲存庫 (git remote)。本機已完成更新，待綁定 remote 後即可一鍵推送上線。")

if __name__ == "__main__":
    main()
