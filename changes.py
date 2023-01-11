import requests
from bs4 import BeautifulSoup
import json
import re
import os

def get_changes(date, built):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8'
    }

    params = (
        ('__func', 'getSubstViewerDayDataHtml'),
    )

    data = '{"__args":[null,{"date":"' + date + '","mode":"classes"}],"__gsh":"00000000"}'

    url = {
        "А": "https://gim5cheb.edupage.org/substitution/server/viewer.js",
        "Т": "https://gym5cheb.edupage.org/substitution/server/viewer.js"
    }[built]

    changes = {}

    r = requests.post(url, headers=headers, params=params, data=data)
    soup = BeautifulSoup(json.loads(r.text)["r"], "lxml")

    classBlock = soup.find_all(class_="section print-nobreak")

    for block in classBlock:
        if block.find(class_="info").find(class_="print-font-resizable").text == "Для этого дня замен нет.":
            return {}

        clas = block.find(class_="print-font-resizable").text
        grade, symbol, built = re.findall(r"(\d+) *(\w) */ *(\w)", clas)[0]
        grade = int(grade)

        changesList = block.find_all(class_="row change")

        blockList = list()
        for change in changesList:
            lessonNumber = change.find(class_="period").text
            changeInfo = change.find(class_="info").text

            blockList.append({"period": lessonNumber, "info": changeInfo})

        changes[f"{grade}{symbol}/{built}"] = blockList

    return changes
