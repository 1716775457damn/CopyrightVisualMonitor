"""
核心入口 main.py
组织所有调度模块：Model -> PageJudger -> OCR -> Exporter -> GUI
"""
import threading
import sys
import tkinter as tk

from page_judger import PageJudger
from exporter import Exporter
from browser_utils import start_edge
from gui_main import MainGUI

from tkinter import filedialog
from navigator_r11 import execute_r11_registration
import os
import glob
import re

def discover_material_files(folder_path):
    txt_files = glob.glob(os.path.join(folder_path, "*软件信息*.txt"))
    code_pdfs = glob.glob(os.path.join(folder_path, "*源代码文档*.pdf"))
    doc_pdfs = glob.glob(os.path.join(folder_path, "*软件著作权*.pdf"))
    if not doc_pdfs:
        doc_pdfs = glob.glob(os.path.join(folder_path, "*文档*.pdf"))
    
    if not txt_files:
        raise FileNotFoundError("未找到包含'软件信息'的 TXT 文件")
    if not code_pdfs:
        raise FileNotFoundError("未找到包含'源代码文档'的 PDF 文件")
    if not doc_pdfs:
        raise FileNotFoundError("未找到包含'软件著作权文档'或'文档'的 PDF 文件")
        
    return txt_files[0], code_pdfs[0], doc_pdfs[0]

def parse_software_info(txt_path):
    data = {}
    key_mapping = {
        "软件全称": "software_name",
        "版本号": "version",
        "开发的硬件环境": "dev_hardware",
        "运行的硬件环境": "run_hardware",
        "开发该软件的操作系统": "dev_os",
        "软件开发环境 / 开发工具": "dev_tools",
        "该软件的运行平台 / 操作系统": "run_platform",
        "软件运行支撑环境 / 支持软件": "support_software",
        "编程语言": "language",
        "源程序量": "source_lines",
        "开发目的": "dev_purpose",
        "面向领域 / 行业": "target_domain",
        "软件的主要功能": "main_functions",
        "技术特点": "tech_features"
    }
    
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(txt_path, 'r', encoding='gbk') as f:
            content = f.read()
            
    matches = re.finditer(r'【(.+?)】[：:]?\s*([^\n]+)', content)
    for match in matches:
        key = match.group(1).strip()
        value = match.group(2).strip()
        if key in key_mapping:
            data[key_mapping[key]] = value
            
    # Parsing the "生成时间：" date line
    time_match = re.search(r'生成时间[：:]\s*([0-9/]+)', content)
    if time_match:
        # Expected format like 2025/10/19, let's keep it as is or change to 2025-10-19 if the site prefers
        time_str = time_match.group(1).replace('/', '-')
        data['dev_finish_date'] = time_str
            
    return data

class AppCore:
    def __init__(self, gui: MainGUI):
        self.gui = gui
        
        self.exporter = Exporter()
        self.page_judger = None
        self.process = None
        self.materials_dir = None
        
    def init_browser(self):
        if not self.process:
            self.gui.log("正在启动或激活本地 Edge 浏览器...")
            target_url = "https://register.ccopyright.com.cn/account.html?current=soft_register"
            self.process = start_edge(target_url)
            self.page_judger = PageJudger(
                logger_callback=self.gui.log,
                username=self.gui.config.get("username", ""),
                password=self.gui.config.get("password", "")
            )
        
    def require_login(self):
        """由 Judger 回调请求登录验证阻塞"""
        event = threading.Event()
        self.gui.ask_for_login(event)
        self.gui.log(">>> 请在弹出的浏览器中手动完成图形验证...")
        event.wait() # 阻塞当前子线程直到用户点确定
        self.gui.log("用户已确认验证完成，继续读取。")
        
    def run_flow(self):
        try:
            # 0. 请求用户选择材料文件夹
            self.gui.log("等待用户选择软著申请材料文件夹...")
            self.materials_dir = filedialog.askdirectory(title="请选择包含TXT和PDF的软著材料文件夹")
            if not self.materials_dir:
                self.gui.log("用户取消了文件夹选择，中止任务。")
                self.gui.set_button_state(False)
                return
                
            self.gui.log(f"已选择材料文件夹: {self.materials_dir}")

            # 1. 初始化
            self.init_browser()
            
            # 2. 页面状态确认流转
            self.gui.log("开始进行页面图像 OCR 状态扫描...")
            is_ready = self.page_judger.process_flow(require_login_callback=self.require_login)
            
            if not is_ready:
                self.gui.log("未能进入系统页面，请检查网络或重试。")
                return
                
            self.gui.update_status("执行自动登记申请流程...")
            
            try:
                txt_path, code_pdf_path, doc_pdf_path = discover_material_files(self.materials_dir)
                parsed_data = parse_software_info(txt_path)
                self.gui.log(f"成功解析信息: {parsed_data.get('software_name', '')} {parsed_data.get('version', '')}")
            except Exception as e:
                self.gui.log(f"解析材料失败：{e}")
                self.gui.update_status("材料解析失败退回", stop_progress=True)
                return
            
            # 3. 使用 Playwright 接管执行精准自动化导航和登记按钮点击
            success = execute_r11_registration(parsed_data, code_pdf_path, doc_pdf_path, logger=self.gui.log)
            
            if success:
                self.gui.log("本次自动化进入 R11 登记页面任务分配成功！请继续后续操作...")
                self.gui.update_status("已进入发证表单", stop_progress=True)
            else:
                self.gui.log("R11登记入口进入失败。")
                self.gui.update_status("自检失败退回", stop_progress=True)
            
            self.gui.log("本次监控任务圆满成功！")
            self.gui.update_status("自检空闲中 (任务完成)", stop_progress=True)
            
        except Exception as e:
            self.gui.log(f"执行异常发生: {e}")
            self.gui.update_status("自检失败退回", stop_progress=True)
        finally:
            self.gui.set_button_state(False)

def main():
    import ttkbootstrap as ttkb
    
    # 使用 ttkbootstrap 现代暗黑系主题 "superhero" 注入主窗口
    root = ttkb.Window(themename="superhero")
    
    app = AppCore(None) # 先占位
    
    gui = MainGUI(root, start_callback=app.run_flow)
    app.gui = gui # 回传
    
    root.mainloop()

if __name__ == "__main__":
    main()
