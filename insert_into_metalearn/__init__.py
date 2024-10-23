import connection
import json
import os
from datetime import datetime


def insert_quiz_from_file(path: str, subject_code: str):
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            if isinstance(data, dict) and 'Object' in data and 'details' in data['Object']:
                print('Start insert from', path)

                quizzes = data['Object']['details']
                quiz_length = len(quizzes)
                created_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if quiz_length == 0:
                    return

                connection.insert_exam_header(
                    data['Code'],
                    data['ExamName'],
                    quiz_length,
                    subject_code,
                    created_time,
                )

                for quiz in quizzes:
                    json_data = json.dumps(quiz['AnswerData'])

                    connection.insert_exam_detail(
                        quiz['Code'],
                        data['Code'],
                        created_time,
                    )

                    connection.insert_quiz_by_sql(
                        quiz['Code'],
                        quiz['Content'],
                        subject_code,
                        json_data,
                        created_time,
                    )

        except json.JSONDecodeError:
            print("Error decoding JSON from file")


def insert_quiz_from_dir(dir_path: str):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                subject_code = get_subject_code(file)

                insert_quiz_from_file(file_path, subject_code)
                connection.update_subject_management_quiz_length(subject_code)
                connection.update_subject_management_exam_length(subject_code)

        connection.commit()


def get_subject_code(text: str) -> str:
    for i in range(1, 6):  # từ N1 đến N5
        if f'N{i}' in text:
            return f'JP_N{i}'

    return 'JP_N5'


insert_quiz_from_dir(r'D:\1.Project\QuizCrawler\crawl_data\trac-nghiem')
