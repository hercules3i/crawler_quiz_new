import pyodbc
import requests
import re

server = '192.168.1.68, 1437'
database = 'SmartWork_MetaLearn'
username = 'admin'
password = 'Vietnam@799'
driver = '{ODBC Driver 13 for SQL Server}'

cursor = None


def remove_special_characters(text):
    return re.sub(r'[^A-Za-z0-9]', '', text)


def create_connection():
    conn = pyodbc.connect(
        f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
    )
    global cursor
    cursor = conn.cursor()

    return cursor


def commit():
    global cursor
    if not cursor:
        create_connection()

    cursor.commit()


def update_subject_management_quiz_length(subject_code: str):
    global cursor

    if not cursor:
        create_connection()

    sql_query = '''
        UPDATE LMS_SUBJECT_MANAGEMENT
        SET COUNT_QUIZ = (
            SELECT COUNT(ID) 
            FROM QUIZ_POOL
            WHERE QUIZ_POOL.SUBJECT_CODE = LMS_SUBJECT_MANAGEMENT.SUBJECT_CODE
        )
        WHERE SUBJECT_CODE=?
    '''
    values = subject_code
    cursor.execute(sql_query, values)


def update_subject_management_exam_length(subject_code: str):
    global cursor

    if not cursor:
        create_connection()

    sql_query = '''
        UPDATE LMS_SUBJECT_MANAGEMENT
        SET COUNT_EXAM = (
            SELECT COUNT(ID) 
            FROM LMS_PRACTICE_TEST_HEADER 
            WHERE LMS_PRACTICE_TEST_HEADER.SUBJECT_CODE = LMS_SUBJECT_MANAGEMENT.SUBJECT_CODE
        )
        WHERE SUBJECT_CODE=?
    '''
    values = subject_code
    cursor.execute(sql_query, values)


def insert_exam_header(exam_code: str, exam_title: str, num_quiz: int, subject_code: str, created_time: str):
    sql_query = '''
        INSERT INTO LMS_PRACTICE_TEST_HEADER(
            PRACTICE_TEST_CODE, PRACTICE_TEST_TITLE, DESCRIPTION, DURATION, UNIT, 
            LEVEL, MARK_TOTAL, NUM_QUIZ, STATUS, CREATED_BY,
            CREATED_TIME, IS_DELETED, SUBJECT_CODE, IS_OFFLINE, IS_PUBLISHED,
            VIEW_RESULT, REWORK, WORK_SEQUENCE, RATING_LOG, HASH_TAG,
            NORMALIZED_TITLE
        )
        VALUES(
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?
        )
    '''

    values = (
        exam_code, exam_title, '', 60, 'MINUTE',
        'NORMAL', '100', num_quiz, 'PASS', 'admin',
        created_time, 0, subject_code, 0, 0,
        0, 0, 0, 'null', '',
        remove_special_characters(exam_title)
    )

    cursor.execute(sql_query, values)
    print('Inserted exam header', exam_title, exam_code)


def insert_exam_detail(quiz_code: str, exam_code: str, created_time: str):
    sql_query = '''
        INSERT INTO LMS_PRACTICE_TEST_DETAIL(
            QUEST_CODE, PRACTICE_TEST_CODE, MARK, DURATION, UNIT,
            CREATED_BY, CREATED_TIME, IS_DELETED
        )
        VALUES(
            ?, ?, ?, ?, ?,
            ?, ?, ?
        )
    '''

    values = (
        quiz_code, exam_code, 2, 1, 'MINUTE',
        'admin', created_time, 0
    )

    cursor.execute(sql_query, values)
    print('Inserted exam detail', quiz_code, exam_code)


def insert_quiz_by_sql(code: str, content: str, subject_code: str, json_data: str, created_time: str):
    global cursor

    if not cursor:
        create_connection()

    if not cursor:
        print('Connection cursor is None')
        return

    sql_query = '''
        INSERT INTO QUIZ_POOL (
            CODE, CONTENT, JSON_DATA, CREATED_BY, SUBJECT_CODE,
            TYPE, PIC_DEEPLINK, IS_DELETED, CREATED_TIME, HAS_CORRECT_ANSWER,
            HASH_TAG, JSON_CANVAS, SOLVE, RATING_LOG, UNIT,
            LEVEL
        )
        VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?
        )
    '''

    values = (
        code, content, json_data, 'admin', subject_code,
        'QUIZ_SING_CH', 'https://admin.metalearn.vn/MobileLogin/InsertQuizJson', '0', created_time, '1',
        '', '', '[]', 'null', '',
        '',
    )

    cursor.execute(sql_query, values)
    print('Inserted quiz', code)


def insert_quiz_by_api(code: str, content: str, subject_code: str, json_data: str):
    print("init insert quiz")

    response = requests.post(
        'https://admin.metalearn.vn/MobileLogin/InsertQuizJson',
        json={
            "Code": code,
            "Content": content,
            "JsonCanvas": "",
            "SubjectCode": subject_code,
            "Type": "QUIZ_SING_CH",
            "Level": "",
            "Unit": "MINUTE",
            "HashTag": "",
            "Duration": "10",
            "Solve": "[]",
            "JsonData": json_data,
            "HasCorrectAnswer": False,
            "CreatedBy": "admin",
            "PicDeeplink": "https://admin.metalearn.vn/uploads/tempFile/Q_IMAGE_25122023-1025.jpeg",
            "RefBlogId": ""
        }
    )
    print(response.content.decode('utf-8'))

