import os


def rename_files(folder_path):
    """
    将文件夹中的文件按照递增数字重命名
    """
    file_count = 0
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            # 获取文件扩展名
            ext = os.path.splitext(filename)[1]
            # 生成新的文件名
            new_filename = f"{file_count:04d}{ext}"
            # 构建新的文件路径
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            # 重命名文件
            os.rename(old_path, new_path)
            file_count += 1


# 调用函数，传入要处理的文件夹路径
rename_files("C:/path/to/your/folder")
