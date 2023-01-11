import requests

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    # Requests sorts cookies= alphabetically
    # 'Cookie': '__ddg1_=JEn0mm3l4ToAaKYQYyP9; sessionId=f9c5db7a-7e89-55d2-0a29-d3c569d8988b',
    'Origin': 'http://os.fipi.ru',
    'Referer': 'http://os.fipi.ru/tasks/2/a',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.124 YaBrowser/22.9.5.710 Yowser/2.5 Safari/537.36',
    'sessionId': 'f9c5db7a-7e89-55d2-0a29-d3c569d8988b',
}

json_data = {
    'taskId': 4043,
    'answer': {
        'TaskType': {
            'Code': 3,
            'Name': 'InputTextMany',
        },
        'Answers': [
            {
                'Number': '1',
                'Text': '34',
                'Type': 'Simple',
            },
        ],
    },
}


response = requests.post('http://os.fipi.ru/api/tasks/CheckAnswer', headers=headers, json=json_data)
print(response.text)