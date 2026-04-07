import mss
import cv2
import numpy as np
import pytesseract
import os
import ctypes
import platform

if platform.system() == "Windows":
    try:
        # 修复高分屏下绝对坐标系与mss截图物理坐标系不匹配的问题
        ctypes.windll.user32.SetProcessDPIAware()  
    except Exception:
        pass

# 显式配置 tesseract.exe 路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe'
# 显式配置 tessdata 路径
os.environ['TESSDATA_PREFIX'] = os.path.abspath('tessdata')

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1] # 截取主显示器
        img = np.array(sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) # OpenCV标准的BGR格式

def find_text_on_screen(img, target_text, lang='chi_sim', binarize=False):
    """使用 Tesseract OCR 查找指定文本在屏幕上的坐标中心"""
    # 预处理：灰度化以提高识别率
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    scale = 1.0
    if binarize:
        # 针对浅色/浅蓝色分页器文字，放大两倍并进行反相二值化提取
        scale = 2.0
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        _, gray = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # 获取详细的检测数据，包括坐标
    # --psm 11 适合寻找稀疏零散的文本段落
    data = pytesseract.image_to_data(gray, lang=lang, config='--psm 11', output_type=pytesseract.Output.DICT)
    
    all_texts = []
    # 重组所有的text并记录每个字符的包围盒
    valid_boxes = []
    for i in range(len(data['text'])):
        text = str(data['text'][i]).replace(' ', '').strip()
        if text:
            all_texts.append(text)
            for char in text:
                valid_boxes.append({
                    'char': char,
                    'x': int(data['left'][i] / scale),
                    'y': int(data['top'][i] / scale),
                    'w': int(data['width'][i] / scale),
                    'h': int(data['height'][i] / scale)
                })
            
    full_ocr_str = "".join(b['char'] for b in valid_boxes)
    
    # 用滑动窗口的形式在合成的字符串里寻找 target_text
    idx = full_ocr_str.find(target_text)
    if idx != -1:
        # 找到了，计算联合Bounding Box
        match_boxes = valid_boxes[idx:idx+len(target_text)]
        min_x = min(b['x'] for b in match_boxes)
        min_y = min(b['y'] for b in match_boxes)
        max_x = max(b['x'] + b['w'] for b in match_boxes)
        max_y = max(b['y'] + b['h'] for b in match_boxes)
        
        cx = min_x + (max_x - min_x) // 2
        cy = min_y + (max_y - min_y) // 2
        return (cx, cy), (min_x, min_y, max_x - min_x, max_y - min_y), all_texts

    return None, None, all_texts
