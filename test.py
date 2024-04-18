import cv2
import numpy as np

from ocr_read import get_bounding_rect

# 创建 EasyOCR 读取器
# reader = easyocr.Reader(['ch_sim'])


image = cv2.imread("assets/other/wm1(sm).jpg")

# adjust_hsv_params(image)

# 转换到 HSV 颜色空间
hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 提取白色区域
lower_white = np.array([87, 104, 0])
upper_white = np.array([180, 255, 255])
white_mask = cv2.inRange(hsv_img, lower_white, upper_white)

cv2.imshow('white_mask', white_mask)
cv2.waitKey(0)

contours, hierarchy = cv2.findContours(white_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

all_rects = []
for cnt in contours:
    if not cv2.contourArea(cnt) > 500:
        continue
    x, y, w, h = cv2.boundingRect(cnt)
    if x > w/2 or y < h/2:
        continue
    all_rects.append((x, y, w, h))

x, y, w, h = get_bounding_rect(all_rects)
# 框选区域
cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

cv2.imshow('result', image)
cv2.waitKey(0)

exit()
