import json
import os
from pyquery import PyQuery as pq
import uuid
from utils import convert_to_filename
from crawler_http import http_get


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

    print("Init crawl_exam_detail from", url)

    html_str = http_get(url)
    if len(html_str) == 0:
        return

    html = pq(html_str)

    quizzes = []
    current_title = ''
    current_title_html = ''

    print("Start getting exam content")
    exam_contents = html('#newsInner > *')

    print("Start looping through elements")

    for child in exam_contents:
        quiz_doc = pq(child)
        tag_name = quiz_doc[0].tag
        class_name = quiz_doc.attr('class')

        if tag_name == 'table' and quiz_doc.hasClass('jp'):
            title = quiz_doc('tbody tr td')
            current_title = title.text()
            current_title_html = title.html()

        if class_name == 'clearfix chanle cauhoi-wrap':
            if current_title:
                # Lấy câu hỏi
                question = quiz_doc.find('.cauhoi').html()  # Giữ nguyên thẻ HTML
                question = current_title_html + '<br />' + question

                # Lấy đáp án
                answers = quiz_doc.find('.answer')
                answer_list = []

                for answer in answers:
                    answer_html = pq(answer).parent().html()
                    answer_text = pq(answer).text()
                    answer_class = pq(answer).attr('class')
                    is_answer = 'd' in answer_class
                    if answer_text != "" and answer_text!= None:
                        answer_list.append({
                            'Code': uuid.uuid4(),  # Tạo UUID
                            'Answer': answer_html,
                            'Type': 'Text',
                            'ContentDecode': answer_text,
                            'IsAnswer': is_answer
                        })

                # Lưu vào object (dictionary)
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


def store_as_json(path: str, subject_name: str, title: str, exam_name: str, quizzes):
    print('Start store json file ', path)

    # Lưu dữ liệu vào file JSON
    with open(path, 'w', encoding='utf-16') as f:
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

