import os

import easyocr

from ocr_read import ocr_read_white, ocr_read_transparent
from utils import walk_dir


if __name__ == "__main__":
    file_path_list = walk_dir("./assets")
    print(file_path_list)

    # 创建 EasyOCR 读取器
    reader = easyocr.Reader(['ch_sim'])

    for (index, img_path) in enumerate(file_path_list):
        origin_file_name = img_path.split('\\')[-1]
        content_name = ocr_read_transparent(img_path, reader)
        if content_name is None:
            content_name = ocr_read_white(img_path, reader)
        print(f"{origin_file_name}: {content_name}")
        # 重命名
        base_path = os.path.dirname(img_path)
        target_file_path = '{}/{} {}.jpg'.format(base_path, content_name, index)
        if not os.path.exists(target_file_path):
            print(f'before: {img_path}')
            print(f'after: {target_file_path}')
            os.rename(img_path, target_file_path)
            print('renamed {} => {}'.format(img_path, target_file_path))
        else:
            print('{} exists! skip...'.format(target_file_path))
