import pytesseract
from PIL import Image
import cv2
import re


def find_UT_time(img):

    # 裁切左下角日期與數字的區域
    h, w, _ = img.shape
    crop = img[int(h*0.975):h-1, 1:int(w*0.13)]  # 根據觀察比例裁切

    # 灰階化與二值化
    # we don't need it
    # gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    thresh = cv2.threshold(crop, 150, 255, cv2.THRESH_BINARY)[1]

    # OCR 參數
    # custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789:/PMUTD. '
    custom_config = r'--oem 3 --psm 7 -c load_system_dawg=0 -c load_freq_dawg=0 -c preserve_interword_spaces=1 -c tessedit_char_whitelist=0123456789:/APMUTD. '

    # 執行 OCR
    text = pytesseract.image_to_string(thresh, config=custom_config, lang='eng')

    s = text.strip()
    s = re.sub(r'(?i)\bUT(.?)',
           lambda m: "UT " + m.group(1) if m.group(1).isdigit() else "UT ",
           text)
    #s = re.sub(r'(?i)\bUT(?=\d)', 'UT ', s)                    # UT 後補空白
    s = re.sub(r'(\d{4})(?=\d{1,2}:\d{2}:\d{2})', r'\1 ', s)   # 年份後補空白
    s = re.sub(r'(?i)(\d)(?=[AP]M\b)', r'\1 ', s)              # 時間與 AM/PM 間補空白
    #print(s)  # UT 12/29/2024 9:19:03 PM

    return s

