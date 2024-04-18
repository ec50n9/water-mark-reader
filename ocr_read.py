import re

import cv2
import easyocr
import numpy as np

from extract_info import extract_info_transparent, extract_info_white


def get_bounding_rect(rects):
    """
    计算包裹多个矩形的最小矩形

    参数:
    rects (list): 一个包含多个矩形(x, y, w, h)的列表

    返回值:
    tuple: 包裹所有矩形的最小矩形(x, y, w, h)
    """
    if not rects:
        return 0, 0, 0, 0

    # 初始化最大和最小坐标
    min_x = min(rect[0] for rect in rects)
    min_y = min(rect[1] for rect in rects)
    max_x = max(rect[0] + rect[2] for rect in rects)
    max_y = max(rect[1] + rect[3] for rect in rects)

    # 计算包裹矩形的宽度和高度
    width = max_x - min_x
    height = max_y - min_y

    return min_x, min_y, width, height


def ocr_read_white(file_path: str, reader: easyocr.Reader):
    image = cv2.imread(file_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        if not cv2.contourArea(cnt) > 5000:
            continue

        x, y, w, h = cv2.boundingRect(cnt)

        if y < h / 2 or x > w / 2:
            continue

        # print(f"x: {x}, y: {y}, w: {w}, h: {h}, area: {w * h}")
        # 框选区域
        # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 裁剪图片
        roi = image[y:y + h, x:x + w]

        # 使用 EasyOCR 识别区域中的文字
        result = reader.readtext(roi)
        # 识别结果
        all_text = ''
        for text in result:
            all_text += re.sub(r'\s+', '', text[1])
        # print(f'全部: {all_text}')
        info = extract_info_white(all_text)
        if info:
            return f"{info['time']} - {info['content']}"
    return None


def ocr_read_transparent(file_path: str, reader: easyocr.Reader):
    image = cv2.imread(file_path)
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([100, 10, 50])
    upper_blue = np.array([130, 255, 255])

    mask = cv2.inRange(hsv_img, lower_blue, upper_blue)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    all_rects = []
    for cnt in contours:
        if not cv2.contourArea(cnt) > 5000:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        all_rects.append((x, y, w, h))

    min_x, min_y, width, height = get_bounding_rect(all_rects)
    roi = image[min_y:min_y + height, min_x:min_x + width]
    _, thresh = cv2.threshold(roi, 240, 255, cv2.THRESH_BINARY)

    # 使用 EasyOCR 识别区域中的文字
    result = reader.readtext(thresh)
    all_text = ''
    for text in result:
        all_text += re.sub(r'\s+', '', text[1])
    info = extract_info_transparent(all_text)
    if info:
        return f"{info.get('time')} - {info.get('content')}"
    return None


def ocr_read_white2(file_path: str, reader: easyocr.Reader):
    image = cv2.imread(file_path)
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_white = np.array([87, 104, 0])
    upper_white = np.array([180, 255, 255])
    white_mask = cv2.inRange(hsv_img, lower_white, upper_white)
    contours, hierarchy = cv2.findContours(white_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    all_rects = []
    for cnt in contours:
        if not cv2.contourArea(cnt) > 500:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        if x > w/2 or y < h/2:
            continue
        all_rects.append((x, y, w, h))

    min_x, min_y, width, height = get_bounding_rect(all_rects)
    roi = image[min_y:min_y + height, min_x:min_x + width]

    cv2.imshow('white_mask', white_mask)
    cv2.waitKey(0)

    _, thresh = cv2.threshold(roi, 240, 255, cv2.THRESH_BINARY)

    # 使用 EasyOCR 识别区域中的文字
    result = reader.readtext(thresh)
    all_text = ''
    for text in result:
        all_text += re.sub(r'\s+', '', text[1])
    info = extract_info_transparent(all_text)
    if info:
        return f"{info.get('time')} - {info.get('content')}"
    return None
