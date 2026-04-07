"""
Tkinter 现代 ttkbootstrap 主题界面
包含侧边栏配置、主界面日志输出、进度条及大号蓝色运行按钮
"""
import tkinter as tk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import messagebox, scrolledtext
import threading
import os
import sys
from datetime import datetime
import config_manager


class MainGUI:
    def __init__(self, root, start_callback):
        self.root = root
        self.start_callback = start_callback
        
        self.root.title("CopyrightVisualMonitor v2.1 - 智能软著自检助手")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        self.font_title  = ("Microsoft YaHei UI", 22, "bold")
        self.font_h2     = ("Microsoft YaHei UI", 12, "bold")
        self.font_label  = ("Microsoft YaHei UI", 10)
        self.font_mono   = ("Consolas", 10)
        
        self.config = config_manager.load_config()
        self.create_widgets()
        
    def create_widgets(self):
        # ── 顶部横幅 ──────────────────────────────────────────
        top_frame = ttkb.Frame(self.root, bootstyle="primary")
        top_frame.pack(fill=X)
        
        lbl_title = ttkb.Label(
            top_frame,
            text="🚀 版权中心全自动视觉监控系统",
            font=self.font_title,
            bootstyle="inverse-primary",
            padding=(20, 25)
        )
        lbl_title.pack()

        # ── 主体内容 ─────────────────────────────────────────────
        content_frame = ttkb.Frame(self.root, padding=20)
        content_frame.pack(fill=BOTH, expand=YES)

        # ── 左侧配置面板 ─────────────────────────────────────────
        left_frame = ttkb.Frame(content_frame)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 20))
        left_frame.configure(width=320)
        left_frame.pack_propagate(False)

        # 1. 账号配置卡片
        frame_account = ttkb.Labelframe(left_frame, text=" 👤 凭据管理 ", padding=15, bootstyle="primary")
        frame_account.pack(fill=X, pady=(0, 15))

        ttkb.Label(frame_account, text="用户名 / 手机号:", font=self.font_label).pack(anchor=W)
        self.var_username = tk.StringVar(value=self.config.get("username", ""))
        ttkb.Entry(frame_account, textvariable=self.var_username).pack(fill=X, pady=(5, 10))

        ttkb.Label(frame_account, text="登录密码:", font=self.font_label).pack(anchor=W)
        self.var_password = tk.StringVar(value=self.config.get("password", ""))
        self.entry_pwd = ttkb.Entry(frame_account, textvariable=self.var_password, show="●")
        self.entry_pwd.pack(fill=X, pady=(5, 5))

        self._pwd_visible = False
        self.btn_eye = ttkb.Button(frame_account, text="👁 显示密码", bootstyle="link", command=self._toggle_pwd)
        self.btn_eye.pack(anchor=E)

        # 2. 运行参数
        frame_conf = ttkb.Labelframe(left_frame, text=" ⚙️ 引擎调优 ", padding=15, bootstyle="secondary")
        frame_conf.pack(fill=X, pady=(0, 20))

        ttkb.Label(frame_conf, text="动作延迟因子:", font=self.font_label).pack(anchor=W)
        slider_row = ttkb.Frame(frame_conf)
        slider_row.pack(fill=X, pady=5)
        self.var_conf = tk.DoubleVar(value=self.config.get("delay_rate", 1.0))
        ttkb.Scale(slider_row, from_=0.5, to_=3.0, variable=self.var_conf, bootstyle="success").pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        ttkb.Label(slider_row, textvariable=self.var_conf, font=("Consolas", 10, "bold"), width=3).pack(side=LEFT)

        # 3. 操作区
        self.btn_start = ttkb.Button(left_frame, text="🚀  开始全自动巡检", bootstyle="success", padding=15, command=self.on_start)
        self.btn_start.pack(fill=X, pady=(0, 15))

        # 4. 状态反馈
        state_frame = ttkb.Frame(left_frame)
        state_frame.pack(fill=X, side=BOTTOM)
        
        self.var_progress = tk.StringVar(value="😴  系统就绪")
        ttkb.Label(state_frame, textvariable=self.var_progress, font=self.font_label, bootstyle="secondary", wraplength=280).pack(anchor=W, pady=5)
        
        self.progress_bar = ttkb.Progressbar(state_frame, bootstyle="success-striped", mode="indeterminate")

        # ── 右侧监控面板 ─────────────────────────────────────────
        right_frame = ttkb.Frame(content_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=YES)

        # 监控组头部
        header_row = ttkb.Frame(right_frame)
        header_row.pack(fill=X, pady=(0, 10))
        
        ttkb.Label(header_row, text="💻  实时巡检监控总线", font=self.font_h2, bootstyle="secondary").pack(side=LEFT)
        
        ttkb.Button(header_row, text="🗑 清空日志", bootstyle="outline-secondary", command=self.clear_logs, padding=(10, 2)).pack(side=RIGHT)

        # 日志文本框
        self.txt_log = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=self.font_mono,
            bg="#0f172a", fg="#10b981",
            insertbackground="white",
            relief="flat",
            padx=15, pady=15,
            borderwidth=0
        )
        self.txt_log.pack(fill=BOTH, expand=YES)

    def _toggle_pwd(self):
        self._pwd_visible = not self._pwd_visible
        self.entry_pwd.config(show="" if self._pwd_visible else "●")
        self.btn_eye.config(text="🙈 隐藏密码" if self._pwd_visible else "👁 显示密码")

    def log(self, text):
        def append():
            timestamp = datetime.now().strftime("[%H:%M:%S] ")
            self.txt_log.insert(tk.END, timestamp + text + "\n")
            self.txt_log.see(tk.END)
        self.root.after(0, append)

    def clear_logs(self):
        self.txt_log.delete(1.0, tk.END)
        self.log("日志已清空")

    def update_status(self, text, start_progress=False, stop_progress=False):
        def update():
            self.var_progress.set(text)
            if start_progress:
                if not self.progress_bar.winfo_ismapped():
                    self.progress_bar.pack(fill=X, pady=5)
                    self.progress_bar.start(10)
            if stop_progress:
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
        self.root.after(0, update)

    def set_button_state(self, is_running):
        def update():
            if is_running:
                self.btn_start.config(state=tk.DISABLED, text="🛡️ 自动巡检运行中...")
            else:
                self.btn_start.config(state=tk.NORMAL, text="🚀  开始全自动巡检")
        self.root.after(0, update)

    def ask_for_login(self, blocking_event):
        def show_dialog():
            messagebox.showinfo("⚠️ 人工介入提示", "由于检测到登录验证码，请在浏览器中手动完成拼图。\n\n处理完后回到此处点击【确定】继续。")
            blocking_event.set()
        self.root.after(0, show_dialog)

    def on_start(self):
        self.config["username"] = self.var_username.get().strip()
        self.config["password"] = self.var_password.get().strip()
        self.config["delay_rate"] = self.var_conf.get()
        config_manager.save_config(self.config)
        
        self.set_button_state(True)
        self.update_status("🔄 引擎正在启动...", start_progress=True)
        self.log("--- 启动新一轮自检任务 ---")
        
        threading.Thread(target=self.start_callback, daemon=True).start()
