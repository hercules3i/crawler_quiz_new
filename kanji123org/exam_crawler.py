import json
import os
from pyquery import PyQuery as pq
import uuid
from utils import convert_to_filename
from crawler_http import http_get
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

def handle_redirect_to_result_page(url):
    browser.get(url)
    time.sleep(2)
    get_result_btn = browser.find_element(By.XPATH, '/html/body/div[6]/section/div/div/div/div[1]/div/form/div[21]/button')
    print(get_result_btn.tag_name)
    browser.execute_script("arguments[0].click();", get_result_btn)    
    time.sleep(2)
    page_html = browser.page_source

    # Tạo file HTML và ghi nội dung vào đó
    with open('result_page.html', 'w', encoding='utf-8') as file:
        file.write(page_html)
    
    return page_html


def uuid_to_str(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def is_exam_exist(file_path: str) -> bool:
    if not os.path.exists(file_path):
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            if isinstance(data, dict) and 'Object' in data and 'details' in data['Object']:
                quiz_length = len(data['Object']['details'])

                if quiz_length > 0:
                    return True
        except json.JSONDecodeError:
            return False

    return False


def handle_exam_detail_html(dir_path: str, exam_name: str, url: str):
    
    file_path = dir_path + '/' + convert_to_filename(exam_name) + '.json'

    if is_exam_exist(file_path):
        print('File', file_path, 'already exist')
        return
    html = handle_redirect_to_result_page(url)
    print("Init crawl_exam_detail from", url)

    # html_str = http_get(url)
    # if len(html_str) == 0:
    #     return
    with open('result_page.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    doc = pq(html_content)

    content_detail = doc('div.content-detail-result')

    if content_detail:
        for child in content_detail.children():
            child_pq = pq(child)  
            question_number = child_pq('div.div-question_number .question_number').text().strip()
            question_content = child_pq('div.div-question-content .question_number_content').text().strip()
            answers = []
            for answer in child_pq('div.answer_answer'):
                answer_text = pq(answer).text().strip()  # Lấy văn bản và loại bỏ khoảng trắng
                is_correct = "true" in pq(answer).attr('class')  # Kiểm tra class để xác định câu trả lời đúng
                answers.append({'answer': answer_text, 'is_correct': is_correct})
            result = {
                'question_number': question_number,
                'question_content': question_content,
                'answers': answers
            }

            print(result)
            

    # for child in exam_contents:
    #     quiz_doc = pq(child)
    #     print(quiz_doc)

    #     if tag_name == 'table' and quiz_doc.hasClass('jp'):
    #         title = quiz_doc('tbody tr td')
    #         current_title = title.text()
    #         current_title_html = title.html()

    #     if class_name == 'clearfix chanle cauhoi-wrap':
    #         if current_title:
    #             # Lấy câu hỏi
    #             question = quiz_doc.find('.cauhoi').html()  # Giữ nguyên thẻ HTML
    #             question = current_title_html + '<br />' + question

    #             # Lấy đáp án
    #             answers = quiz_doc.find('.answer')
    #             answer_list = []

    #             for answer in answers:
    #                 answer_html = pq(answer).parent().html()
    #                 answer_text = pq(answer).text()
    #                 answer_class = pq(answer).attr('class')
    #                 is_answer = 'd' in answer_class

    #                 answer_list.append({
    #                     'Code': uuid.uuid4(),  # Tạo UUID
    #                     'Answer': answer_html,
    #                     'Type': 'Text',
    #                     'ContentDecode': answer_text,
    #                     'IsAnswer': is_answer
    #                 })

    #             # Lưu vào object (dictionary)
    #             quiz = {
    #                 'Id': len(quizzes) + 1,
    #                 'Order': "40",
    #                 'Duration': 10,
    #                 'Unit': "MINUTE",
    #                 'Mark': 10,
    #                 'Content': question,
    #                 'Solve': {
    #                     'Solver': '',
    #                     'SolveMedia': []
    #                 },
    #                 'QuestionMedia': [],
    #                 'Code': uuid.uuid1(),
    #                 'Type': 'QUIZ_SING_CH',
    #                 'AnswerData': answer_list,
    #                 'IdQuiz': 75,
    #                 'UserChoose': None
    #             }
    #             quizzes.append(quiz)

    # if len(quizzes) > 0:
    #     store_as_json(
    #         file_path,
    #         current_title,
    #         current_title,
    #         exam_name,
    #         quizzes
    #     )


def store_as_json(path: str, subject_name: str, title: str, exam_name: str, quizzes):
    print('Start store json file ', path)

    # Lưu dữ liệu vào file JSON
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(
            {
                'ID': None,
                'SubjectName': subject_name,
                'Title': title,
                'ExamName': exam_name,
                'Error': False,
                'Object': {
                    'isAlreadyDone': False,
                    'details': quizzes
                },
                'Code': uuid.uuid4(),
            },
            f,
            ensure_ascii=False,
            indent=4,
            default=uuid_to_str
        )

