import re

import cv2
import numpy as np
import easyocr

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


image = cv2.imread("assets/wm7.jpg")
hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# lower_blue = np.array([100, 50, 50])
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

    # 框选区域
    # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    print(f"x: {x}, y: {y}, w: {w}, h: {h}, area: {w * h}")

min_x, min_y, width, height = get_bounding_rect(all_rects)
# cv2.rectangle(image, (min_x, min_y), (min_x + width, min_y + height), (0, 0, 255), 2)

roi = image[min_y:min_y + height, min_x:min_x + width]

_, thresh = cv2.threshold(roi, 240, 255, cv2.THRESH_BINARY)
cv2.imshow('test', thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 使用 EasyOCR 识别区域中的文字
result = reader.readtext(thresh)
# 识别结果
all_text = ''
for text in result:
    all_text += re.sub(r'\s+', '', text[1])
print(f"全部: {all_text}")
match = re.search(r'施工内容:(.*?)施工区域', all_text)
if match:
    name = match.group(1)
    print(f"识别结果：{name}")
else:
    print("识别失败")

window_height = 1200
window_width = int(image.shape[1] * (window_height / image.shape[0]))
cv2.namedWindow("res", cv2.WINDOW_NORMAL)
cv2.resizeWindow("res", window_width, window_height)
cv2.imshow('res', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
