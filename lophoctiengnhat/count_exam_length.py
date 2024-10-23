import os
import json


def count_json_elements(directory):
    total_exam = 0
    total_elements = 0
    to_remove = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, dict) and 'Object' in data and 'details' in data['Object']:
                            quiz_length = len(data['Object']['details'])

                            if quiz_length > 0:
                                total_elements += quiz_length
                                total_exam += 1
                            else:
                                to_remove.append(file_path)

                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from file: {file_path}")

    # for path in to_remove:
    #     os.remove(path)
    #     print('removed ', path)

    print("Exam length: ", total_exam)
    print("Quiz length: ", total_elements)


directory = '../crawl_data/trac-nghiem'  # Thay thế bằng đường dẫn đến thư mục của mày
count_json_elements(directory)
