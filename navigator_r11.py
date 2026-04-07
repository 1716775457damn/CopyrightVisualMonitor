import logging
import re
import time
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

def smart_click(page: Page, selector: str, description: str, timeout=10000, logger=print):
    """
    智能点击：尝试多次，包含滚动和等待
    """
    logger(f"尝试点击: {description}...")
    try:
        locator = page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        locator.scroll_into_view_if_needed()
        time.sleep(0.5)
        locator.click(timeout=timeout)
        return True
    except Exception as e:
        logger(f"⚠️ 点击 {description} 失败: {e}")
        return False

def smart_fill(page: Page, selector: str, value: str, description: str, timeout=10000, logger=print):
    """
    智能填写
    """
    logger(f"尝试填写 {description}: {value}...")
    try:
        locator = page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        locator.fill(value, timeout=timeout)
        return True
    except Exception as e:
        logger(f"⚠️ 填写 {description} 失败: {e}")
        return False

def execute_r11_registration(parsed_data: dict, code_pdf_path: str, doc_pdf_path: str, logger=print) -> bool:
    """
    Connects to an existing Edge browser on port 9222 and performs
    precise navigation and clicking for the R11 software registration using pure JS.
    """
    with sync_playwright() as p:
        try:
            logger("正在通过 CDP (端口9222) 连接至 Edge 浏览器...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            
            context = browser.contexts[0]
            target_page = None
            
            # 清理多余标签页
            for page in context.pages:
                if any(k in page.url for k in ["register.ccopyright", "register.html", "account.html"]):
                    if target_page is None:
                        target_page = page
                    else:
                        try: page.close()
                        except: pass
                elif any(k in page.url for k in ["newtab", "about:blank"]):
                    try: page.close()
                    except: pass
            
            if not target_page:
                logger("❌ 未能在浏览器中找到版权登记官网标签页。")
                return False

            target_page.bring_to_front()
            logger("✅ 成功接管版权官网页面，开始自动导航...")

            # 1. 导航到“版权登记”并点击
            if not smart_click(target_page, "text=版权登记", "【版权登记】菜单", logger=logger):
                return False
            target_page.wait_for_timeout(1000)
            
            # 2. 点击“计算机软件著作权相关登记”
            sub_xpath = "xpath=/html/body/div[2]/div[2]/div[2]/div/div/img[1]"
            if not smart_click(target_page, sub_xpath, "“计算机软件著作权相关登记”图片", logger=logger):
                # 尝试备选方案：按文本选择
                if not smart_click(target_page, "text=计算机软件著作权相关登记", "“计算机软件著作权相关登记”文本", logger=logger):
                    return False
            target_page.wait_for_timeout(1000)
            
            # 3. 点击 R11 立即登记按钮
            r11_xpath = "xpath=/html/body/div[2]/div[2]/div[3]/div/table/tr[1]/td[1]/div/div[3]/button"
            if not smart_click(target_page, r11_xpath, "R11 【立即登记】按钮", logger=logger):
                return False
            
            logger("✅ 已成功击中 R11 【立即登记】按钮！")
            target_page.wait_for_timeout(2000)
            
            # --- 以下进入软著信息填写流程表单阶段 ---
            logger("====== 开始自动填写软著登记表单 (第1页) ======")
            
            # 须知页
            smart_click(target_page, "xpath=/html/body/div[2]/div[2]/div[2]/div/div[1]", "须知页下一步", logger=logger)
            target_page.wait_for_timeout(1000)

            # 软件全称 & 版本号
            smart_fill(target_page, "xpath=/html/body/div[2]/div[2]/div[2]/div[2]/div[1]/div/div[1]/div/input", parsed_data.get('software_name', ''), "软件全称", logger=logger)
            smart_fill(target_page, "xpath=/html/body/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[1]/div/input", parsed_data.get('version', ''), "版本号", logger=logger)
            
            smart_click(target_page, "xpath=/html/body/div[2]/div[2]/div[2]/div[4]/button[2]", "第1页下一步", logger=logger)
            target_page.wait_for_timeout(1500)

            logger("====== 开始自动填写软著登记表单 (第2页) ======")
            
            # 软件分类
            smart_click(target_page, "xpath=/html/body/div[2]/div[2]/div[2]/div[1]/div/div/div[1]", "软件分类下拉框", logger=logger)
            target_page.wait_for_timeout(500)
            smart_click(target_page, "xpath=/html/body/div[2]/div[2]/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]", "应用软件选项", logger=logger)
            
            # 开发完成日期
            finish_date = parsed_data.get('dev_finish_date', '')
            if finish_date and '-' in finish_date:
                parts = finish_date.split('-')
                if len(parts) == 3:
                    year_val, month_val, day_val = parts[0], parts[1].lstrip('0'), parts[2].lstrip('0')
                    try:
                        date_input_xpath = "xpath=/html/body/div[2]/div[2]/div[2]/div[4]/div/div/div/div[1]"
                        smart_click(target_page, date_input_xpath, "打开日期面板", logger=logger)
                        target_page.wait_for_timeout(800)
                        
                        popup_base = "xpath=/html/body/div[2]/div[2]/div[2]/div[4]/div/div/div/div[3]"
                        
                        # 选择年份
                        smart_click(target_page, f"{popup_base}/div/div[1]/div/div[1]/div[1]", "年份选择头", logger=logger)
                        target_page.wait_for_timeout(500)
                        target_page.locator(popup_base).locator("div, span, td").filter(has_text=re.compile(f"^{year_val}年?$")).first.click()
                        
                        # 选择月份
                        target_page.wait_for_timeout(500)
                        smart_click(target_page, f"{popup_base}/div/div[1]/div/div[2]/div[1]", "月份选择头", logger=logger)
                        target_page.wait_for_timeout(500)
                        target_page.locator(popup_base).locator("div, span, td").filter(has_text=re.compile(f"^{month_val}月?$")).first.click()
                        
                        # 选择日期
                        target_page.wait_for_timeout(500)
                        target_page.locator(f"{popup_base}/div/div[2]/div/table").locator("td").filter(has_text=re.compile(f"^{day_val}$")).first.click()
                        
                        logger(f"✅ 日期 {finish_date} 选择成功。")
                    except Exception as e:
                        logger(f"⚠️ 自动日期选择失败: {e}")
            
            smart_click(target_page, "xpath=/html/body/div[2]/div[2]/div[2]/div[7]/button[2]", "第2页下一步", logger=logger)
            target_page.wait_for_timeout(1500)
            
            logger("====== 开始自动填写软著登记表单 (第3页) ======")
            fields = [
                ("/html/body/div[2]/div[2]/div[2]/div[1]/div/div/textarea", 'dev_hardware', "开发硬件环境"),
                ("/html/body/div[2]/div[2]/div[2]/div[2]/div/div/textarea", 'run_hardware', "运行硬件环境"),
                ("/html/body/div[2]/div[2]/div[2]/div[3]/div/div/textarea", 'dev_os', "开发操作系统"),
                ("/html/body/div[2]/div[2]/div[2]/div[4]/div/div/textarea", 'dev_tools', "开发软件工程"),
                ("/html/body/div[2]/div[2]/div[2]/div[5]/div/div/textarea", 'run_platform', "运行平台"),
                ("/html/body/div[2]/div[2]/div[2]/div[6]/div/div/textarea", 'support_software', "支撑软件"),
                ("/html/body/div[2]/div[2]/div[2]/div[7]/div/div[2]/textarea", 'language', "编程语言"),
                ("/html/body/div[2]/div[2]/div[2]/div[8]/div/div/div[1]/div/input", 'source_lines', "源程序量"),
                ("/html/body/div[2]/div[2]/div[2]/div[9]/div/div/textarea", 'dev_purpose', "开发目的"),
                ("/html/body/div[2]/div[2]/div[2]/div[10]/div/div/textarea", 'target_domain', "面向领域"),
                ("/html/body/div[2]/div[2]/div[2]/div[11]/div/div/textarea", 'main_functions', "主要功能"),
                ("/html/body/div[2]/div[2]/div[2]/div[12]/div/div[2]/textarea", 'tech_features', "技术特点"),
            ]
            for xpath, key, desc in fields:
                smart_fill(target_page, f"xpath={xpath}", parsed_data.get(key, ''), desc, logger=logger)
            
            smart_click(target_page, "xpath=/html/body/div[2]/div[2]/div[2]/div[16]/button[2]", "第3页下一步", logger=logger)
            
            logger("✅ 表单填写完毕！请手动上传鉴别材料...")
            
            # 等待提交按钮出现
            submit_btn_xpath = "xpath=/html/body/div[2]/div[2]/div[2]/div[4]/button[3]"
            while True:
                try:
                    target_page.locator(submit_btn_xpath).wait_for(state="visible", timeout=2000)
                    logger("✅ 侦测到最后提交按钮！开始自动完成提交...")
                    break
                except: pass
                target_page.wait_for_timeout(1000)

            # 自动提交
            smart_click(target_page, submit_btn_xpath, "保存并提交申请", logger=logger)
            target_page.wait_for_timeout(3000)
            
            # 打印签章页
            print_seal_xpath = "xpath=/html/body/div[2]/div[2]/div[2]/div/div/div/div[2]/button[1]"
            pages_before = len(context.pages)
            smart_click(target_page, print_seal_xpath, "打印签章页", logger=logger)
            target_page.wait_for_timeout(3000)
            
            operate_page = target_page
            if len(context.pages) > pages_before:
                operate_page = context.pages[-1]
                operate_page.wait_for_load_state()
            
            # 打印确认
            smart_click(operate_page, "xpath=/html/body/div[2]/div[2]/div/div/div[1]/button", "打印（确认）", logger=logger)
            target_page.wait_for_timeout(1500)
            smart_click(operate_page, "xpath=/html/body/div[2]/div[2]/div/div/div[1]/button[2]", "二次确认打印", logger=logger)
            
            logger("🎉 全流程自动化任务执行完毕！")
            return True

        except Exception as e:
            logger(f"❌ 运行异常: {e}")
            if 'target_page' in locals() and target_page:
                try: target_page.screenshot(path="debug_error.png")
                except: pass
            return False
