#!/usr/bin/env python
"""
启动脚本 - 同时启动后端和简单的前端服务器
"""
import subprocess
import sys
import os
import time
import webbrowser
import threading
from pathlib import Path

# 项目根目录（保证工作目录正确，且子进程 stdout 不使用 PIPE，避免缓冲区塞满导致进程卡死）
ROOT = Path(__file__).resolve().parent

# Windows 上 5500 易出现 WinError 10013（被占用或权限），改用非常见端口；若仍冲突可改此数字
FRONTEND_PORT = 8765

def start_backend():
    """启动FastAPI后端"""
    print("🚀 启动后端服务...")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=ROOT,
    )

def start_frontend():
    """启动简单的前端服务器"""
    print("🌐 启动前端服务...")
    return subprocess.Popen(
        [
            sys.executable, "-m", "http.server", str(FRONTEND_PORT),
            "--bind", "127.0.0.1",
            "--directory", "frontend",
        ],
        cwd=ROOT,
    )

def open_browser():
    """等待几秒后打开浏览器"""
    time.sleep(5)
    url = f"http://127.0.0.1:{FRONTEND_PORT}"
    webbrowser.open(url)
    print(f"✅ 浏览器已打开，访问 {url}")

def check_backend_ready():
    """检查后端服务是否就绪"""
    import urllib.request
    import urllib.error
    
    url = "http://127.0.0.1:8000"
    max_retries = 10
    retry_delay = 1
    
    for i in range(max_retries):
        try:
            response = urllib.request.urlopen(url, timeout=2)
            if response.getcode() == 200:
                return True
        except urllib.error.URLError:
            pass
        time.sleep(retry_delay)
    
    return False

def main():
    print("=" * 50)
    print("🎯 AI面试系统启动中...")
    print("=" * 50)
    
    # 启动后端
    backend_process = start_backend()
    print("✅ 后端服务启动中 (http://127.0.0.1:8000)")
    
    # 等待后端启动并检查状态
    print("⏳ 正在等待后端服务就绪...")
    if check_backend_ready():
        print("✅ 后端服务已就绪")
    else:
        print("❌ 后端服务启动超时，请检查日志")
    
    # 启动前端
    frontend_process = start_frontend()
    print(f"✅ 前端服务启动中 (http://127.0.0.1:{FRONTEND_PORT})")
    
    # 打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("\n💡 按 Ctrl+C 停止所有服务\n")
    
    try:
        # 等待进程结束
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()