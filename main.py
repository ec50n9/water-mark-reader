import os
import re
import datetime

import cv2
import easyocr
import numpy as np

# 创建 EasyOCR 读取器
reader = easyocr.Reader(['ch_sim'])


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


def extract_info_white(text):
    """
    从给定的文本中提取出施工内容、施工责任人、拍摄时间和天气。

    参数:
    text (str): 包含相关信息的文本。

    返回:
    dict: 包含提取出的信息的字典,键包括'content', 'person', 'time', 'weather'。
    """

    # 使用正则表达式匹配相关信息
    pattern = r'施工内容:(.*?)施工责任人:(.*?)拍摄时间:(.*?)天气:(.*?)$'
    match = re.search(pattern, text)

    if match:
        content = match.group(1).strip()
        person = match.group(2).strip()
        time = match.group(3).strip()
        weather = match.group(4).strip()

        # 将拍摄时间解析为年月日时分
        dt = datetime.datetime.strptime(time, "%Y.%m.%d%H:%M")
        time = dt.strftime("%Y-%m-%d %H:%M")

        return {
            'content': content,
            'person': person,
            'time': time,
            'weather': weather
        }
    else:
        return None


def extract_info_transparent(text:str):
    """
    从给定的文本中提取出施工内容、施工责任人、拍摄时间和天气。

    参数:
    text (str): 包含相关信息的文本。

    返回:
    dict: 包含提取出的信息的字典,键包括'content', 'person', 'time', 'weather'。
    """

    # 使用正则表达式匹配相关信息
    pattern = r'施工内容:(.*?)施工区域:(.*?)施工负责人:(.*?)拍摄时间:(.*?)地点'
    match = re.search(pattern, text)

    if match:
        content = match.group(1).strip()
        local = match.group(2).strip()
        person = match.group(3).strip()
        time = match.group(4).strip()

        # 将拍摄时间解析为年月日时分
        dt = datetime.datetime.strptime(time, "%Y.%m.%d%H:%M")
        time = dt.strftime("%Y-%m-%d %H:%M")

        return {
            'content': content,
            'person': person,
            'time': time,
            'local': local
        }
    else:
        return None


def ocr_read_white(file_path: str):
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


def ocr_read_transparent(file_path: str):
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


def walk_dir(path: str):
    result_files = []
    for root, dirs, files in os.walk(path):
        result_files.extend([os.path.join(root, file_name) for file_name in files])
        for dir_name in dirs:
            result_files.extend(walk_dir(os.path.join(root, dir_name)))
    return result_files


if __name__ == "__main__":
    file_path_list = walk_dir("./assets")
    print(file_path_list)
    for (index, img_path) in enumerate(file_path_list):
        origin_file_name = img_path.split('\\')[-1]
        content_name = ocr_read_white(img_path)
        if content_name is None:
            content_name = ocr_read_transparent(img_path)
        print(f"{origin_file_name}: {content_name}")
