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
    with open('crawl_data/kanji123org/category_list.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

        for category_section in data:
            for category in category_section['categories']:
                cat_name = category['name']
                cat_url = category['url']

                print('Start fetch from', cat_url)
                response = requests.get(cat_url)
                if response.status_code != 200:
                    print(f"Failed to retrieve data: {response.status_code}")

                html_string = response.content.decode('utf8')
                handle_category_html(cat_name, html_string)
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
    category_content = html('.main *')

    list_exams = []
    list_categories = {}
    n2_exams = []
    n3_exams = []
    n4_exams = []
    n5_exams = []
    for child in category_content:
        el = pq(child)
        if el.is_('a') and 'Đề' in el.text():
            print(f"Text: {el.text()}, Href: {el.attr('href')}")
            url = el.attr('href')
            # url = url.replace("https://kanji123.org/", "https://kanji123.org/result/")

            list_exams.append({
                "name": el.text(),
                "url": url
            })
    for exam in list_exams:
        if "N2" in exam["name"]:
            n2_exams.append(exam)
        elif "N3" in exam["name"]:
            n3_exams.append(exam)
        elif "N4" in exam["name"]:
            n4_exams.append(exam)
        elif "N5" in exam["name"]:
            n5_exams.append(exam)
    list_categories["N2"] = n2_exams
    list_categories["N3"] = n3_exams
    list_categories["N4"] = n4_exams
    list_categories["N5"] = n5_exams
    dest_path = os.path.join("crawl_data", "kanji123org","trac-nghiem")
    for category, exams in list_categories.items():
        print(f"Cấp độ {category}: {len(exams)} bài thi")
        title = f"Kiểm tra Kanji {category}"
        name = name.replace(" ","_")
        news_path = f"{dest_path}/{name}-{category}.json"
        store_as_json(news_path,title,exams)