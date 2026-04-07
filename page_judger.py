"""
页面逻辑调度器 (OpenCV + PyTesseract + PyAutoGUI 纯视觉版本)
通过全屏截图、OCR识别文本坐标来实现页面导航，并加入自动输入账号密码逻辑。
"""
import cv2
import time
import pyautogui
import os
import platform
import win32api
from datetime import datetime

# 导入模块化组件
from vision_engine import capture_screen, find_text_on_screen
from captcha_solver import CaptchaSolver

class PageJudger:
    def __init__(self, logger_callback=print, username="", password=""):
        self.log = logger_callback
        self.username = username
        self.password = password
        self.captcha_solver = CaptchaSolver(logger_callback=logger_callback)

    def interruptible_servo_move(self, target_cx, target_cy, click=True):
        """
        持续纠正鼠标位置，渐渐逼近目标坐标（基于绝对坐标系）。
        如果期间检测到用户人为移动了鼠标(发生位置偏移)，则抛出中断信号返回 False。
        """
        self.log(f"启动辅助随动，引导鼠标至 ({target_cx}, {target_cy})...")
        last_mx, last_my = pyautogui.position()
        
        for _ in range(50):
            mx, my = pyautogui.position()
            
            # 检测人为干预 (欧氏距离>15视为用户外部介入)
            dist_user = ((mx - last_mx)**2 + (my - last_my)**2)**0.5
            if dist_user > 15:
                self.log("【中断】检测到防抖阈值以上的外部动作，系统中止接管交还给您！")
                return False
                
            dx = target_cx - mx
            dy = target_cy - my
            dist_target = (dx**2 + dy**2)**0.5
            
            if dist_target <= 5:
                # 已经足够靠近，执行到达点击
                if click: 
                    pyautogui.click()
                time.sleep(0.1)
                return True
                
            # 计算步长（比例控制系统，逐渐逼近减速防止冲过头）
            move_x = int(dx * 0.35)
            move_y = int(dy * 0.35)
            if move_x == 0 and dx != 0: move_x = 1 if dx > 0 else -1
            if move_y == 0 and dy != 0: move_y = 1 if dy > 0 else -1
                
            pyautogui.move(move_x, move_y, duration=0.01)
            last_mx, last_my = pyautogui.position()
            
        return False

    def process_flow(self, require_login_callback):
        self.log("分析页面当前状态...")
        for attempt in range(4):
            time.sleep(2.5) # 渲染缓冲时间
            img = capture_screen()
            
            # 状态1：核心提取页
            center, _, _ = find_text_on_screen(img, "全部", lang='chi_sim')
            if center:
                soft_center, _, _ = find_text_on_screen(img, "软件登记", lang='chi_sim')
                if soft_center:
                    self.log("成功定位到核心软件登记列表页。")
                    return True

            # 状态2：在首页但未进入系统
            top_login_center, _, _ = find_text_on_screen(img, "登录", lang='chi_sim')
            if top_login_center and top_login_center[1] < 150:
                self.log("在首页且未登录，点击头部登录按钮...")
                self.interruptible_servo_move(top_login_center[0], top_login_center[1])
                time.sleep(2)
                continue
                
            # 状态3：在系统内但未点击软件登记
            soft_nav_center, _, _ = find_text_on_screen(img, "软件登记", lang='chi_sim')
            if soft_nav_center:
                self.log("登录成功，点击左侧【软件登记】菜单...")
                self.interruptible_servo_move(soft_nav_center[0], soft_nav_center[1])
                continue
                
            # 状态4：未登录，并位于登录面板页
            login_panel_center, _, all_texts = find_text_on_screen(img, "账号登录", lang='chi_sim')
            pwd_login_center, _, _ = find_text_on_screen(img, "密码登录", lang='chi_sim')
            
            if login_panel_center or pwd_login_center or (top_login_center and top_login_center[1] >= 150):
                self.log("检测到登录面板，准备先行自动输入账号密码...")
                
                user_hint_center, _, _ = find_text_on_screen(img, "用户名", lang='chi_sim')
                
                if user_hint_center:
                    target_cx = user_hint_center[0]
                    target_cy = user_hint_center[1]
                    
                    reached = self.interruptible_servo_move(target_cx, target_cy, click=True)
                    if reached:
                        self.log("瞄准账号框，开始输入账号...")
                        pyautogui.typewrite(self.username, interval=0.03)
                        time.sleep(0.3)
                        
                        pwd_hint_center, _, _ = find_text_on_screen(img, "入密码", lang='chi_sim')
                        if not pwd_hint_center:
                            pwd_hint_center, _, _ = find_text_on_screen(img, "请密码", lang='chi_sim')
                        if pwd_hint_center:
                            self.log("移动至密码框，准备输入密码...")
                            self.interruptible_servo_move(pwd_hint_center[0], pwd_hint_center[1], click=True)
                            pyautogui.typewrite(self.password, interval=0.03)
                            time.sleep(0.3)
                            
                    login_btn_center, _, _ = find_text_on_screen(img, "即登录", lang='chi_sim')
                    if login_btn_center:
                        self.log("将鼠标移动至【立即登录】并点击...")
                        self.interruptible_servo_move(login_btn_center[0], login_btn_center[1], click=True)
                        time.sleep(2)
                        
                        if self.captcha_solver.solve_slider_captcha():
                            self.log("滑块验证码处理完毕，等待页面跳转...")
                            time.sleep(3)
                            continue 

                    self.log("账号 and 密码均已顺畅输入完毕！")
            
            self.log("已暂停视觉控制！此时您可以移动鼠标接管并进行滑动拼图验证...")
            require_login_callback()
            continue
        else:
            if attempt == 3:
                 self.log("最后一次重试，保存调试截图和OCR日志...")
                 cv2.imwrite("debug_last_screen.png", img)
                 with open("debug_ocr_texts.txt", "w", encoding="utf-8") as f:
                     f.write("\n".join(all_texts))
                 self.log("识别到的文本已保存到 debug_ocr_texts.txt。")

        self.log("多次重试仍未能定位到有效页面。")
        return False

    def read_core_data(self):
        """关键节点：在【全部】标签页，翻页提取所有软件记录并去重"""
        self.log("开始在【全部】标签页提取所有连续页的软件登记信息...")
        time.sleep(2)
        
        tab_names = ["待受理", "待审查", "待补正", "待发放", "已发放"]
        summary = {k: 0 for k in tab_names}
        all_parsed_records = []
        
        img = capture_screen()
        
        self.log("点击标签页：全部...")
        tab_center, _, _ = find_text_on_screen(img, "全部", lang='chi_sim')
        if tab_center:
            self.interruptible_servo_move(tab_center[0], tab_center[1], click=True)
            time.sleep(1.5)
            img = capture_screen()
            
        current_page = 1
        last_page_raw_text = ""
        
        while True:
            self.log(f"--- 正在提取第 {current_page} 页 ---")
            records, current_raw_text = self._extract_records_from_screen(img, f"全部_页{current_page}", return_raw=True)
            self.log(f"  第 {current_page} 页提取到 {len(records)} 条记录")
            
            if current_page > 1 and current_raw_text and current_raw_text == last_page_raw_text:
                self.log("【终极查重】当前页面的提取文本与上一页一字不差，结束翻页。")
                break
                
            last_page_raw_text = current_raw_text
            
            if records:
                all_parsed_records.extend(records)
                    
            if current_page > 1 and records:
                existing_serials = set(r.get('流水号') for r in all_parsed_records if r.get('流水号'))
                current_serials = set(r.get('流水号') for r in records if r.get('流水号'))
                if current_serials and current_serials.issubset(existing_serials):
                    self.log("【全局查重】检测到本页所有数据均已提取过，结束循环。")
                    break
            
            next_page_num = str(current_page + 1)
            pyautogui.click(pyautogui.size()[0]//2, pyautogui.size()[1]//2)
            for _ in range(4):
                pyautogui.press('pagedown')
                time.sleep(0.1)
            time.sleep(0.5)
            
            img_bottom = capture_screen()
            h, w = img_bottom.shape[:2]
            crop_y_start = int(h * 0.30)
            crop_y_end = int(h * 0.95)
            img_bottom_cropped = img_bottom[crop_y_start:crop_y_end, :]
            
            next_btn_center, _, _ = find_text_on_screen(img_bottom_cropped, ">", lang='eng+chi_sim', binarize=True)
            
            if not next_btn_center:
                next_btn_center, _, _ = find_text_on_screen(img_bottom_cropped, next_page_num, lang='eng+chi_sim', binarize=True)
            
            if next_btn_center:
                real_x = next_btn_center[0]
                real_y = next_btn_center[1] + crop_y_start
                
                success = self.interruptible_servo_move(real_x, real_y, click=True)
                
                if not success:
                    self.log("【动作中断】工作流已暂停运行！请手动点击“下一页”并按左键恢复...")
                    while True:
                        if win32api.GetAsyncKeyState(0x01) < 0:
                            while win32api.GetAsyncKeyState(0x01) < 0:
                                time.sleep(0.05)
                            break
                        time.sleep(0.1)
                
                time.sleep(1.5)
                img = capture_screen()
                current_page += 1
            else:
                self.log("未找到翻页标识，判定为到达末尾。")
                break
        
        unique_records_dict = {}
        for r in all_parsed_records:
            name = r.get("软件名称")
            if not name: continue
                
            date_str = r.get("申请日期", "")
            try:
                current_date = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                current_date = datetime.min
                
            if name not in unique_records_dict or current_date > unique_records_dict[name]["date"]:
                unique_records_dict[name] = {"record": r, "date": current_date}
                
        final_records = [item["record"] for item in unique_records_dict.values()]
        self.log(f"去重后共获得 {len(final_records)} 个独立软件项目的最新状态。")
        
        for r in final_records:
            st = r.get("状态")
            if st:
                summary[st] = summary.get(st, 0) + 1
            
        return summary, final_records, img

    def _extract_records_from_screen(self, img, tab_filter="全部", return_raw=False):
        """使用 Ctrl+A + Ctrl+C 复制页面所有文字"""
        import pyperclip
        try:
            pyperclip.copy("")
        except Exception:
            pass
        
        screen_w, screen_h = pyautogui.size()
        pyautogui.click(screen_w // 2, int(screen_h * 0.55))
        time.sleep(0.4)
        
        pyautogui.hotkey('ctrl', 'home')
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.7)
        
        raw_text = ""
        try:
            raw_text = pyperclip.paste()
        except Exception as e:
            self.log(f"  剪贴板读取失败: {e}")
            
        pyautogui.press('escape')
        time.sleep(0.1)
        
        if not raw_text or len(raw_text) < 50:
            if return_raw: return [], ""
            return []
        
        records = self._parse_clipboard_text(raw_text, tab_filter)
        if return_raw:
            return records, raw_text
        return records
    
    def _parse_clipboard_text(self, raw_text: str, tab_filter: str) -> list:
        """从剪贴板复制的页面文字中解析软件记录"""
        import re
        records = []
        lines = [l.strip() for l in raw_text.replace('\r', '').split('\n') if l.strip()]
        
        STATUS_KEYWORDS = ["待受理", "待审查", "待补正", "待发放", "已发放", "不予办理", "撤回", "已通过"]
        SKIP_KEYWORDS = ["流水号", "登记详情", "申请确认签页", "状态", "操作", "高级筛选", "查询",
                         "软件登记", "作品登记", "我的登记", "我的查询", "我的历史", "历史记录",
                         "历史查询", "软件查询", "作品查询", "撤回申请", "查看详情"]
        
        current_serial = None
        current_name = None
        current_date = None
        current_status = None
        
        for line in lines:
            if any(k == line or k in line for k in SKIP_KEYWORDS):
                if len(line) < 15: continue
            
            serial_m = re.search(r'(20\d{2}\s*[A-Z]\s*\d{2}\s*[A-Z]\s*\d{6,10})(?!\d)', line)
            if serial_m:
                if current_serial and current_name and current_status:
                    records.append({
                        "流水号": current_serial,
                        "软件名称": current_name,
                        "申请日期": current_date or "",
                        "状态": current_status,
                        "标签页": tab_filter
                    })
                current_serial = serial_m.group(1).replace(' ', '')
                current_name = None
                current_status = None
                current_date = None
                date_m = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                if date_m: current_date = date_m.group(1)
                continue
            
            date_m = re.search(r'^(\d{4}-\d{2}-\d{2})$', line)
            if date_m and current_serial:
                current_date = date_m.group(1)
                continue
            
            status_found = False
            for status in STATUS_KEYWORDS:
                if status in line:
                    current_status = status
                    status_found = True
                    break
            if status_found: continue
            
            if (current_serial and not current_name
                    and 4 <= len(line) <= 50
                    and any('\u4e00' <= c <= '\u9fff' for c in line)
                    and not any(k in line for k in STATUS_KEYWORDS + SKIP_KEYWORDS)
                    and not re.match(r'^\d', line)):
                current_name = line
        
        if current_serial and current_name and current_status:
            records.append({
                "流水号": current_serial,
                "软件名称": current_name,
                "申请日期": current_date or "",
                "状态": current_status,
                "标签页": tab_filter
            })
            
        return records
