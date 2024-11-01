import os
import glob
import json
from exam_crawler import handle_exam_detail_html
from utils import convert_to_filename, makedir_if_not_exist


def read_json(path: str):
    # Liệt kê tất cả các tệp JSON trong thư mục
    json_files = glob.glob(os.path.join(path, '*.json'))

    # Khởi tạo một danh sách để lưu trữ nội dung của tất cả các tệp JSON
    all_data_json = []

    # Đọc và phân tích cú pháp từng tệp JSON
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            data['dir_path'] = json_file[:-5]
            all_data_json.append(data)

    return all_data_json


def exam_all_crawler():
    all_json_file = read_json('crawl_data/vnjpclub/trac-nghiem')
    print(len(all_json_file))
    for index, data in enumerate(all_json_file):
        
        dir_path = data['dir_path']
        if "list-N45" in dir_path:
            makedir_if_not_exist(dir_path)

            # Lấy mảng các đối tượng từ khóa 'exams'
            exams_list = data['exams']

            # Lặp qua từng đối tượng trong mảng
            for exam in exams_list:
                name = exam["name"]
                link = exam["url"]
                handle_exam_detail_html(dir_path, name, link)

