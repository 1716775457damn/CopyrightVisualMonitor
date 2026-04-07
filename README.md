<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/OCR-Tesseract-orange.svg" alt="OCR Engine">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform">

  <h1>👁️ CopyrightVisualMonitor v2.1</h1>
  <p><strong>中国版权保护中心软件著作权申请状态全自动纯视觉监控助手</strong></p>
</div>

---

## 💡 简介 (Introduction)

传统的网页爬虫面对复杂的政府网站反爬系统和验证码往往难以维持稳定。本工具采用 **纯视觉定位 (Pure Computer Vision & OCR)** 技术路线，完全模拟真实用户在屏幕前的点击操作，不依赖任何非公开 API，也不拦截网络请求。

本项目通过集成 **OpenCV 图像处理** 和 **Tesseract OCR (文字识别)** 技术构建，实现对中国版权保护中心“我的登记”状态的自动化监控。它能全自动跨表单抓取最新申请进度，提供极高的安全性和稳定性。

### 🌟 核心特性 (Features)

- **🤖 纯视觉驱动**：完全基于屏幕像素识别，规避 DOM 变动或网络层反爬，像真人一样“看”屏幕并操作。
- **🦾 智能 OCR 定位**：内置增强型 Tesseract 识别工作流，支持高 DPI 缩放下的精准文字定位与点击。
- **🛡️ 免登录态重用**：基于 `edge_profile` 自动保存登录状态，只需初次扫码登录，后续可实现长时间免密运行。
- **📊 自动化报表导出**：自动翻页扫描所有软著项，智能去重比对，生成带状态流的 `Excel` 存档报告。
- **📦 绿色便携部署**：提供精简后的 `PyInstaller` 打包机制，可构建不依赖 Python 环境的独立 `.exe` 执行文件。

---

## 🚀 快速开始 (Quick Start)

### 1. 环境准备

本工具建议在 Python 3.11+ 环境下运行：

```bash
# 克隆仓库
git clone https://github.com/your-username/CopyrightVisualMonitor.git
cd CopyrightVisualMonitor

# 安装依赖
pip install -r requirements.txt
```

### 2. 外部引擎配置
- **OCR 引擎**：请安装 [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki)。
  - 确保 `tesseract.exe` 已加入系统环境变量。
  - 将中文训练包 `chi_sim.traineddata` 放入项目 `tessdata` 目录下。
- **本地配置**：将 `config.json.example` 重命名为 `config.json` 并填写相关信息。

### 3. 运行
```bash
python main.py
```
> 或者运行 `gui_main.py` 启动拥有现代 UI 的桌面控制台台。

---

## 🛠️ 打包发布 (Building)

为了方便非开发人员使用，可以使用以下脚本一键打包：
```bash
build_exe.bat
```
生成的单文件可执行程序位于 `dist/` 目录下。

---

## 📂 源码架构 (Architecture)

```text
CopyrightVisualMonitor/
├── main.py                🚩 入口程序与业务流程编排
├── gui_main.py            🎨 ttkbootstrap 现代图形界面
├── vision_engine.py       👁️ OCR 与图像预处理核心模块
├── page_judger.py         🧭 页面引导与视觉追踪控制器
├── navigator_r11.py       🏎️ Playwright 自动化驱动引擎
├── exporter.py            📉 数据处理与 Excel 导出
├── captcha_solver.py      🧩 基于轮廓检测的滑块识别
└── config_manager.py      🔐 安全配置与凭据管理
```

---

## 🎯 常见问题 (FAQ)

**Q：界面无法识别文字或找不到按钮？**
A：请检查 Windows 显示设置中的“缩放比例”。建议设置为 100%。如果必须使用高缩放，请在 `.exe` 属性中开启“替代高 DPI 缩放行为”。

**Q：Tesseract 路径报错？**
A：请手动编辑 `vision_engine.py` 中的 `pytesseract.pytesseract.tesseract_cmd`，确保指向正确的 `tesseract.exe` 安装位置。

---

## 📜 许可 (License)
本项目遵守 [MIT License](./LICENSE)。仅供学习研究使用。
