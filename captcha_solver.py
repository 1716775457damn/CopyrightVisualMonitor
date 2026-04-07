import cv2
import time
import pyautogui
import random
from vision_engine import capture_screen, find_text_on_screen

class CaptchaSolver:
    def __init__(self, logger_callback=print):
        self.log = logger_callback

    def solve_slider_captcha(self):
        """
        自动检测屏幕上的滑块验证码并通过 OpenCV 计算缺口距离进行拟人滑动
        """
        self.log("正在扫描屏幕，等待滑动验证码加载...")
        
        bbox = None
        img = None
        for wait_i in range(10):
            img = capture_screen()
            
            # 抛弃容易被背景水印干扰的“拼图”等字眼，改寻最稳定、字面最清晰的顶部标题“安全验证”
            title_hint, bbox, _ = find_text_on_screen(img, "安全验证", lang='chi_sim')
            if not title_hint:
                title_hint, bbox, _ = find_text_on_screen(img, "请完成", lang='chi_sim')
                
            if title_hint:
                self.log("✅ 发现滑块验证码标题！启动几何锁定与 OpenCV 计算引擎...")
                break
                
            self.log(f"  ...未看到验证码，继续等待加载 ({wait_i+1}/10)")
            time.sleep(2)
            
        if not bbox:
            self.log("当前屏幕始终未检测到滑动验证码的标题特征。")
            return False
            
        for captcha_attempt in range(5):
            self.log(f"✅ 第 {captcha_attempt + 1} 次获取滑块验证码特征...")
            if captcha_attempt > 0:
                img = capture_screen()
                title_hint, bbox, _ = find_text_on_screen(img, "安全验证", lang='chi_sim')
                if not title_hint:
                    title_hint, bbox, _ = find_text_on_screen(img, "请完成", lang='chi_sim')
                
                if not title_hint:
                    self.log("滑块验证码已消失，判定为验证成功！")
                    return True
            
            sx, sy, sw, sh = bbox
            
            # 基于“请完成安全验证”标题的严格几何定位
            img_top = sy + sh + 15
            img_bottom = img_top + 212
            img_left = sx - 20
            img_right = img_left + 340
            
            # 边界安全保护
            h, w = img.shape[:2]
            img_top, img_bottom = max(0, img_top), min(h, img_bottom)
            img_left, img_right = max(0, img_left), min(w, img_right)
            
            captcha_img = img[img_top:img_bottom, img_left:img_right]
            
            gray = cv2.cvtColor(captcha_img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            
            # 假设拼图块在左侧 65 像素内
            slider_width_estimate = 65
            slider_template = edges[:, :slider_width_estimate]
            search_area = edges[:, slider_width_estimate:]
            
            # 纯粹的结构化匹配
            res = cv2.matchTemplate(search_area, slider_template, cv2.TM_CCOEFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            cv2.imwrite(f"debug_captcha_edges_{captcha_attempt}.png", edges)
            
            target_x_offset = max_loc[0] + slider_width_estimate
            self.log(f"🎯 OpenCV 原生计算缺口距离: {target_x_offset} 像素。")
            
            # [精度微调]
            CALIBRATION_OFFSET = 13 
            target_x_offset += CALIBRATION_OFFSET
            self.log(f"🔧 [精度微调] 增加边框偏移量 {CALIBRATION_OFFSET}，最终物理滑动: {target_x_offset} 像素。")
            
            # 定位实际的滑块按钮
            start_x = img_left + 22
            start_y = img_bottom + 22
            
            self.log("开始拟人化拖动滑块...")
            pyautogui.moveTo(start_x, start_y, duration=0.5, tween=pyautogui.easeInOutQuad)
            pyautogui.mouseDown()
            
            current_x = start_x
            remaining_dist = target_x_offset
            
            # 起步
            first_step = int(remaining_dist * 0.6)
            current_x += first_step
            pyautogui.moveTo(current_x, start_y, duration=random.uniform(0.2, 0.4), tween=pyautogui.easeOutQuad)
            
            # 中段
            remaining_dist -= first_step
            second_step = int(remaining_dist * 0.8)
            current_x += second_step
            pyautogui.moveTo(current_x, start_y, duration=random.uniform(0.3, 0.6), tween=pyautogui.easeInOutSine)
            
            # 末段
            remaining_dist -= second_step
            current_x += remaining_dist
            pyautogui.moveTo(current_x, start_y, duration=random.uniform(0.4, 0.8), tween=pyautogui.easeOutBounce)
            
            time.sleep(random.uniform(0.3, 0.5))
            pyautogui.mouseUp()
            
            self.log("拖动完成！等待判断结果...")
            time.sleep(3) 
        
        self.log("滑动验证码连续多次均未能成功，请手动介入！")
        return False
