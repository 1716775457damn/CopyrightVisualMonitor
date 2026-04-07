<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/YOLO-v11%2Fv12-orange.svg" alt="YOLO Models">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform">

  <h1>👁️ CopyrightVisualMonitor v2.1</h1>
  <p><strong>中国版权保护中心软件著作权申请状态全自动纯视觉自检助手</strong></p>
</div>

---

## 💡 简介 (Introduction)

传统的网页爬虫面对复杂的政府网站反爬系统和验证码往往束手无策。本工具**另辟蹊径**，采用 **纯视觉定位 (Computer Vision)** 技术路线，完全模拟真实用户在屏幕前的点击操作。

本项目通过集成 **YOLO 目标检测** 和 **Tesseract OCR (传统边缘提取)** 技术构建，无需依赖任何非公开 API，也无需拦截网络请求。即可实现对中国版权保护中心“我的登记”状态监控，全自动跨表单抓取最新申请进度，提供极高防封安全性与离线持久化机制。

### 🌟 核心特性 (Features)

- **🤖 纯视觉驱动**：使用 OpenCV 和 YOLO 直接"看"屏幕像素，规避 DOM 变动或网络层反爬，极其稳定。
- **🦾 智能操作接管**：内置微观鼠标运动轨迹防抖算法及 Playwright 底层 CDP 连接，无感化自动化填表。
- **🛡️ 状态无缝缓存**：基于 `edge_profile` 缓存文件，只用扫一次验证码即可实现后续彻底免密、无人值守。
- **📊 傻瓜式导出报告**：自动翻页扫描所有软著件，查重比对后生成带有精准状态流的记录报告与本地 `Excel` 存档。
- **📦 一键可执行部署**：自带经过优化的 `PyInstaller` 极速打包脚本（移除无关重担库如 TF/Torch/Scipy），构建最精简的 `.exe`！

---

## 🚀 快速开始 (Quick Start)

### 1. 环境依赖准备

建议使用 `conda` 或系统 `venv` 建立干净的目录，项目完全基于 Python 3.11+。

```bash
# 1. 克隆本仓库到本地
git clone https://github.com/your-username/CopyrightVisualMonitor.git
cd CopyrightVisualMonitor

# 2. 安装 Python 核心框架依赖
pip install -r requirements.txt
```

### 2. 外部必备引擎
- **OCR 引擎**：请确保宿主环境已安装 [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki)。并将其执行路径 `tesseract.exe` 配至系统环境变量，同时将中文和通用语言训练包 (`chi_sim.traineddata` 等) 放至本项目 `tessdata` 文件夹下。
- **本地化配置**：重命名根目录的 `config.json.example` 为 `config.json`，并填入你的版权中心测试账号密码（该文件已加入 `.gitignore` 保护您的安全）。

### 3. 一键启动
```bash
python main.py
```
> 或者你也可以双击 `gui_main.py` 开启拥有现代暗黑美学界面的 Tkinter 控制台。

---

## 🛠️ 构建与发布 (Building Executable)

为了方便普通业务人员使用，只需双击打包脚本：
```bash
> build_exe.bat
```
它会在后台调用精简后的参数进行一站式编译，生成完全脱离 Python 环境的绿色单文件 `dist/CopyrightVisualMonitor_v2.exe`。

---

## 📂 源码架构导读 (Architecture)

```text
CopyrightVisualMonitor/
├── main.py                🚩 核心应用入口与流程编排
├── gui_main.py            🎨 ttkbootstrap 桌面端界面 (自带实时控制台)
├── vision_engine.py       👁️ OpenCV + PyTesseract 混合增强识别控制模块
├── page_judger.py         🧭 自动导航、视觉追踪与重试拦截控制器
├── navigator_r11.py       🏎️ Playwright CDP 接管下的极速表单填写器
├── exporter.py            📉 数据入库及去重、Excel报表生成模块
├── captcha_solver.py      🧩 基于轮廓检测的常见滑块验证码对策模块
├── yolo_detector.py       🧠 YOLO (ONNX) 骨干网推理入口 (高级开发保留)
├── build_exe.bat          📦 无缝化极简打包批处理工具
└── config_manager.py      🔐 凭密脱敏及配置重载模块
```

---

## 🎯 常见问题 (FAQ & Troubleshooting)

**Q：界面无法识别或找不到“全部”/“登录”标签？**
A：我们的图像缩放和反相算法在 Windows 高 DPI 缩放环境下偶尔存在偏差。如果是高分辨率屏幕（如 2K, 4K），请右键 `.exe` -> `属性` -> `兼容性` -> `更改高DPI设置` -> 勾选 `替代高DPI缩放行为：应用程序`。

**Q：终端一直提示 Tesseract 报错崩溃？**
A：请检查 `vision_engine.py` 第一行的 `pytesseract.pytesseract.tesseract_cmd` 路径是否正确指向你本地 `C:\` 下的 `tesseract.exe` 安装位置，同时确保 `tessdata/chi_sim.traineddata` 存在且无损。本期工程由于规避了 AI 大模型依赖导致这一个配置尤为重要。

---

## 🤝 贡献与感谢 (Contributing)
如果你能在此项目的基础上加入更多维度的机器视觉算法训练或是多浏览器扩展包，欢迎在此提交 Pull Request。

## 📜 许可 (License)
本项目遵守 [MIT License](./LICENSE)。在合法、合规的情况下你可以自由研究与分发。
