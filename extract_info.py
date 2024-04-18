import datetime
import re


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
        try:
            dt = datetime.datetime.strptime(time, "%Y.%m.%d%H:%M")
            time = dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            dt = datetime.datetime.strptime(time, "%Y.%m.%d%H;%M")
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
        try:
            dt = datetime.datetime.strptime(time, "%Y.%m.%d%H:%M")
            time = dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            dt = datetime.datetime.strptime(time, "%Y.%m.%d%H;%M")
            time = dt.strftime("%Y-%m-%d %H:%M")

        return {
            'content': content,
            'person': person,
            'time': time,
            'local': local
        }
    else:
        return None