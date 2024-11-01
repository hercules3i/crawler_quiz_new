from pyquery import PyQuery as pq
from time import sleep
import io
import json
import requests
import os
import glob
from utils import convert_to_filename
import time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
# from Task import TaskSimpleData
from selenium.common.exceptions import *
options = Options()
options.add_experimental_option("detach", True)

browser = Chrome(options)
browser.maximize_window()
actionChains = ActionChains(browser)
def test_crawl_exam_list():
    f = io.open('category_template.html', mode='r', encoding='utf-8')
    html = f.read()
    handle_category_html('N1', html)


def list_json_files(directory):
    return glob.glob(os.path.join(directory, '*.json'))


def crawl_all_category():
    with open('crawl_data/vnjpclub/category_list.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

        for category_section in data:
            for category in category_section['categories']:
                cat_name = category['name']
                cat_url = category['url']
                browser.get(cat_url)
                # print('Start fetch from', cat_url)
                # response = requests.get(cat_url)
                # if response.status_code != 200:
                #     print(f"Failed to retrieve data: {response.status_code}")
                page_html = browser.page_source

                # Tạo file HTML và ghi nội dung vào đó
                with open('result_page.html', 'w', encoding='utf-8') as file:
                    file.write(page_html)
                with open('result_page.html', 'r', encoding='utf-8') as file:
                    html_string = file.read()
                # html_string = response.content.decode('utf8')
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
    path = os.path.join("crawl_data","vnjpclub","trac-nghiem")
    dest_path = path + "/" + "list-" + name + ".json"
    category_content = html('.category *')
    print("categoty:",category_content)
    list_exams = []
    list_categories = {}
    n2_exams = []
    n3_exams = []
    n4_exams = []
    n5_exams = []
    
    for child in category_content:
        el = pq(child)
        if el.is_('a') and 'Bài-' in el.text():
            print(f"Text: {el.text()}, Href: {el.attr('href')}")
            url = el.attr('href')
            url = url.replace(".html", "-kiem-tra.html")
            _url = "https://www.vnjpclub.com" + url
            list_exams.append({
                "name": el.text(),
                "url": _url
            })
        if el.is_('a') and 'Tuần' in el.text():
            print(f"Text: {el.text()}, Href: {el.attr('href')}")
            url = el.attr('href')
            _url = "https://www.vnjpclub.com" + url
            list_exams.append({
                "name": el.text(),
                "url": _url
            })
    print(list_exams)
    store_as_json(dest_path,name,list_exams)