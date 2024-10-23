import re
import os


def convert_to_filename(utf8_string: str):
    # Loại bỏ ký tự không hợp lệ
    clean_string = re.sub(r'[^\w\s-]', '', utf8_string)
    # Thay khoảng trắng bằng dấu gạch dưới
    filename = re.sub(r'[\s-]+', '_', clean_string).strip()
    return filename


def makedir_if_not_exist(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
