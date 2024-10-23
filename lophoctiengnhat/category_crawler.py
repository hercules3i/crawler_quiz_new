from pyquery import PyQuery as pq
from time import sleep
import io
import json
import requests
import os
import glob
from utils import convert_to_filename


def test_crawl_exam_list():
    f = io.open('category_template.html', mode='r', encoding='utf-8')
    html = f.read()
    handle_category_html('N1', html)


def list_json_files(directory):
    return glob.glob(os.path.join(directory, '*.json'))


def crawl_all_category():
    with open('crawl_data/lophoctiengnhat/category_list.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

        for category_section in data:
            for category in category_section['categories']:
                cat_name = category['name']
                cat_url = category['url']
                # if "N1" in  cat_name:
                print('Start fetch from', cat_url)
                response = requests.get(cat_url)
                if response.status_code != 200:
                    print(f"Failed to retrieve data: {response.status_code}")

                html_string = response.content.decode('utf8')
                handle_category_html(cat_name, html_string)
                # with open('N1.html', 'w', encoding='utf-8') as file:
                #     file.write(page_html)
                sleep(5)


def store_as_json(path, title, list_exam):
    # path = convert_to_filename(path)

    data = {
        'title': title,
        'exams': list_exam
    }

    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
        print("Stored a json to", path)


def handle_category_html(name: str, html_str: str):
    html = pq(html_str)
    category_content = html('#newsInner *')

    dest_path = 'crawl_data/lophoctiengnhat/trac-nghiem/list-' + name + '-'
    current_section_title = ""
    list_exam = []

    for child in category_content:
        el = pq(child)
        el_name = el[0].tag
        el_class = el.attr('class')
        el_style = el.attr('style')
        if el_name == 'td':
                current_section_title = el.text()
                print("Current section title:", current_section_title)
        if el_class and "effect" in el_class:
                if len(list_exam) > 0:
                    path = dest_path + current_section_title + '.json'
                    store_as_json(path, current_section_title, list_exam)
                    list_exam = []
                    print(f"Stored JSON for {current_section_title}")
        # Kiểm tra nội dung của list_exam trước khi thêm
        if el_class and 'right-link' in el_class and 'long' in el_class:
            exam_name = el('.right-txt').text()
            exam_url = el.attr('href')
            if len(exam_url) > 0:
                list_exam.append({
                    'name': exam_name,
                    'url': 'https://m.lophoctiengnhat.com' + exam_url,
                })
                print(f"Added exam: {exam_name}")

