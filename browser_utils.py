"""
浏览器控制模块
利用 subprocess 启动本机 Edge 浏览器，并通过指定 user-data-dir 实现持久化免密登录
"""
import subprocess
import time
import os
import winreg

def get_edge_path():
    """读取注册表获取系统的 Node Edge 绝对路径"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe")
        path, _ = winreg.QueryValueEx(key, "")
        return path
    except Exception:
        # Fallback 常见路径
        for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", 
                  r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]:
            if os.path.exists(p):
                return p
        raise FileNotFoundError("未找到 Edge 浏览器，请确认已安装。")

def start_edge(url):
    """启动本地 Edge 并导航到指定URL"""
    edge_path = get_edge_path()
    profile_dir = os.path.abspath("edge_profile")
    
    cmd = [
        edge_path,
        f"--user-data-dir={profile_dir}",
        "--remote-debugging-port=9222",
        "--start-maximized",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-restore-session-state",
        "--hide-crash-restore-bubble",
        "--disable-session-crashed-bubble",
        "--disable-features=SessionCrashedBubble,RestoreSessionCrashedBubble",
        url
    ]
    
    try:
        # 为了彻底解决多开标签页的问题，并在避免使用 --app 导致坐标系改变的前提下
        # 我们需要在启动前清理掉可能残留的 Edge 进程 (特别是后台存留的崩溃子进程)
        try:
            # 仅在 windows 下生效，静默杀死 msedge.exe
            subprocess.run(["taskkill", "/F", "/IM", "msedge.exe", "/T"], 
                           capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(1) # 等待释放文件锁
        except Exception:
            pass
            
        process = subprocess.Popen(cmd)
        time.sleep(3) # 缓冲加载时间
        return process
    except Exception as e:
        raise RuntimeError(f"Edge启动失败: {e}")
