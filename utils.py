import os

import cv2


def walk_dir(path: str):
    result_files = []
    for root, dirs, files in os.walk(path):
        result_files.extend([os.path.join(root, file_name) for file_name in files])
        for dir_name in dirs:
            result_files.extend(walk_dir(os.path.join(root, dir_name)))
    result_files = [file_name.replace('\\', '/') for file_name in result_files if file_name.endswith('.jpg') or file_name.endswith('.png')]
    return result_files


def adjust_hsv_params(image):
    # 创建滑动条窗口
    cv2.namedWindow('Adjust Parameters')

    # 定义 HSV 颜色范围的初始值
    h_min = 0
    h_max = 180
    s_min = 0
    s_max = 255
    v_min = 0
    v_max = 255

    def nothing(x):
        pass

    # 创建滑动条
    cv2.createTrackbar('H Min', 'Adjust Parameters', h_min, 180, nothing)
    cv2.createTrackbar('H Max', 'Adjust Parameters', h_max, 180, nothing)
    cv2.createTrackbar('S Min', 'Adjust Parameters', s_min, 255, nothing)
    cv2.createTrackbar('S Max', 'Adjust Parameters', s_max, 255, nothing)
    cv2.createTrackbar('V Min', 'Adjust Parameters', v_min, 255, nothing)
    cv2.createTrackbar('V Max', 'Adjust Parameters', v_max, 255, nothing)

    # 处理图像
    while True:
        # 获取滑动条的当前值
        h_min = cv2.getTrackbarPos('H Min', 'Adjust Parameters')
        h_max = cv2.getTrackbarPos('H Max', 'Adjust Parameters')
        s_min = cv2.getTrackbarPos('S Min', 'Adjust Parameters')
        s_max = cv2.getTrackbarPos('S Max', 'Adjust Parameters')
        v_min = cv2.getTrackbarPos('V Min', 'Adjust Parameters')
        v_max = cv2.getTrackbarPos('V Max', 'Adjust Parameters')

        # 使用当前的 HSV 范围进行图像处理
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (h_min, s_min, v_min), (h_max, s_max, v_max))
        result = cv2.bitwise_and(image, image, mask=mask)

        # 显示结果
        cv2.imshow('Adjust Parameters', result)

        # 等待用户按下 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
