import mss
import cv2
import numpy as np
import pytesseract
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe'

def test_pagination_crop():
    print("准备截图，请在 3 秒内将页面切回软著查询界面并悬停（如果在浏览器里的话）...")
    time.sleep(3)
    
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
    h, w = img.shape[:2]
    # 我们线上代码里的剪裁区域：30% - 95%
    crop_y_start = int(h * 0.30)
    crop_y_end = int(h * 0.95)
    img_cropped = img[crop_y_start:crop_y_end, :]
    
    # 灰度
    gray = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2GRAY)
    
    # OCR
    data = pytesseract.image_to_data(gray, lang='chi_sim', config='--psm 11', output_type=pytesseract.Output.DICT)
    
    found_chars = []
    print("\n--- OCR 解析到的文字及坐标 ---")
    for i in range(len(data['text'])):
        text = str(data['text'][i]).replace(' ', '').strip()
        if text:
            # 记录详细
            print(f"[{text}] -> x:{data['left'][i]}, y:{data['top'][i]}")
            if text in ['共', '页']:
                found_chars.append({'char': text, 'x': data['left'][i], 'y': data['top'][i]})
                
    print(f"\n关键字符查找结果: {found_chars}")
    
    # 绘制框和文字并保存，用来排查到底截取成了什么鬼样子
    for i in range(len(data['text'])):
        text = str(data['text'][i]).replace(' ', '').strip()
        if text:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            if text in ['共', '页']:
                cv2.rectangle(img_cropped, (x, y), (x + w, y + h), (0, 0, 255), 2)
            else:
                cv2.rectangle(img_cropped, (x, y), (x + w, y + h), (0, 255, 0), 1)
                
    cv2.imwrite("debug_pagination_crop.png", img_cropped)
    print("调试图片已保存至当前目录: debug_pagination_crop.png")

if __name__ == "__main__":
    test_pagination_crop()
