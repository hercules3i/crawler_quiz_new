import json
import os
from pyquery import PyQuery as pq
import uuid
from utils import convert_to_filename
# from crawler_http import http_get
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
    try:
        get_result_btn = browser.find_element(By.XPATH, '/html/body/div[1]/section/div[2]/div/div/div/div/div[1]/div[1]/div/div/article/div/div/form/input[3]')
        print(get_result_btn.tag_name)
        browser.execute_script("arguments[0].click();", get_result_btn)    
    except Exception:
        print("Ex:",url)
    time.sleep(0.25)
    page_html = browser.page_source
    with open('result_page.html', 'w', encoding='utf-8') as file:
        file.write(page_html)


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
    file_path = os.path.join(dir_path, convert_to_filename(exam_name) + '.json')

    if is_exam_exist(file_path):
        print('File', file_path, 'already exists')
        return
    
    handle_redirect_to_result_page(url)
    # Giả định bạn đã có nội dung HTML từ trang kết quả
    with open('result_page.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    doc = pq(html_content)
    content_detail = doc('form.quiz-form *')

    if content_detail:
        quizzes = []
        questions = [] 
        tr_count = 0
        div_tracnghiem_count = 0
        current_title = "Kiem tra tieng nhat vnjpclub"
        for child in content_detail:
            
            child_pq = pq(child)
            if "tracnghiem" in str(child_pq) and child.tag == "div" and child_pq.attr("class") == "tracnghiem":
                div_tracnghiem_count += 1
                questions.append(child_pq)
                number_question = child_pq('#question .bai_stt').text().strip().replace("問", "").strip()

                # Lấy nội dung câu hỏi
                question = child_pq('#question b').text().strip()
                answer_list = []
                answers_doc = child_pq("#table_tracnghiem *")
                # Duyệt qua từng hàng trong bảng
                for index in range(1, 5): 
                    tr_count += 1
                    answer_text = answers_doc(f"tr#table_tracnghiem.tr{tr_count} span").text().strip()
                    answer_text = " ".join(dict.fromkeys(answer_text.split()))
                    answer_html = f'<span style="font-size: 15px">{answer_text}</span>'
                    # Kiểm tra nếu thẻ span có id là result_correct_{index} có thẻ img
                    result_correct_id = f"result_correct_{div_tracnghiem_count}{index}"
                    is_answer = bool(answers_doc(f"tr.tr{tr_count} td span#{result_correct_id} img"))
                    answer_list.append({
                        'Code': str(uuid.uuid4()),  # Tạo UUID
                        'Answer': answer_html,
                        'Type': 'Text',
                        'ContentDecode': answer_text,
                        'IsAnswer': is_answer
                    })
                               # In ra danh sách đáp án
                for answer in answer_list:
                    print(answer)
                
                quiz = {
                    'Id': len(quizzes) + 1,
                    'Order': "40",
                    'Duration': 10,
                    'Unit': "MINUTE",
                    'Mark': 10,
                    'Content': question,
                    'Solve': {
                        'Solver': '',
                        'SolveMedia': []
                    },
                    'QuestionMedia': [],
                    'Code': uuid.uuid1(),
                    'Type': 'QUIZ_SING_CH',
                    'AnswerData': answer_list,
                    'IdQuiz': 75,
                    'UserChoose': None
                }
                quizzes.append(quiz)

        if len(quizzes) > 0:
            store_as_json(
                file_path,
                current_title,
                current_title,
                exam_name,
                quizzes
            )

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

