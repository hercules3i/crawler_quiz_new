import os
import glob
import json
from exam_crawler import handle_exam_detail_html
from utils import convert_to_filename, makedir_if_not_exist


def read_json(path: str):
    # Liệt kê tất cả các tệp JSON trong thư mục
    json_files = glob.glob(os.path.join(path, '*.json'))

    all_data_json = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                data['dir_path'] = json_file[:-5]
                all_data_json.append(data)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Lỗi khi đọc tệp {json_file}: {e}")
    return all_data_json


def exam_all_crawler():
    all_json_file = read_json('crawl_data/vnjpclub/trac-nghiem')
    print(f"Tìm thấy {len(all_json_file)} tệp JSON.")

    for index, data in enumerate(all_json_file):
        dir_path = data['dir_path']
        makedir_if_not_exist(dir_path)

        exams_list = data['exams']
        for exam in exams_list:
            name = exam["name"]
            link = exam["url"]
            try:
                handle_exam_detail_html(dir_path, name, link)
            except Exception as e:
                print(f"Lỗi khi xử lý bài thi {name}: {e}")
            sleep(2)  # Đảm bảo không tải quá nhanh


def handle_exam_detail_html(dir_path, name, link):
    response = requests.get(link)

    if response.status_code == 200:
        html_content = response.content
        encoding = response.apparent_encoding or 'utf-8'

        try:
            html_decoded = html_content.decode(encoding)
            file_path = os.path.join(dir_path, convert_to_filename(name) + ".html")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html_decoded)
            print(f"Đã lưu bài thi: {file_path}")
        except UnicodeDecodeError as e:
            print(f"Lỗi mã hóa nội dung từ {link}: {e}")
    else:
        print(f"Không thể truy cập {link}: HTTP {response.status_code}")
