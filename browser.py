import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebFunction:

    # подключение к вебдрайверу
    def __init__(self):
        self.s = Service("D:\\pythonProjects\\gym5bot\\chromedriver.exe")
        self.browser = webdriver.Chrome(service=self.s)
        self.browser.set_window_size(1920, 1080)
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'accept-language': 'en-US,en;q=0.9,ru;q=0.8'
        }
        self.way = {
            "А": "https://gim5cheb.edupage.org/substitution/server/viewer.js",
            "Т": "https://gym5cheb.edupage.org/substitution/server/viewer.js"
        }

    # получение скриншота расписания
    def get_schedule(self, data):
        name, surname, grade, symbol, built = data
        flag = False

        wait = WebDriverWait(self.browser, 10)
        self.browser.get("https://gim5cheb.edupage.org/timetable/")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[title='Учащиеся']")))
        self.browser.find_element(By.CSS_SELECTOR, "[title='Учащиеся']").click()
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class = 'submenu']")))

        if int(grade) > 9:
            for item in self.browser.find_elements(By.CSS_SELECTOR, "[class = 'submenu']"):
                if item.text == f"{grade}/{built}":
                    flag = True
                    item.click()
                    break
        else:
            for item in self.browser.find_elements(By.CSS_SELECTOR, "[class = 'submenu']"):
                if item.text == f"{grade}{symbol}/{built}":
                    flag = True
                    item.click()
                    break
        if not flag:
            return 0

        flag = False

        wait.until(EC.element_to_be_clickable((item)))

        for student in item.find_elements(By.CSS_SELECTOR, "[class = 'dropDownPanel asc-context-menu'] li"):
            if f"{surname} {name}" in student.text:
                flag = True
                student.click()
                break

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class = 'print-nobreak']")))
        schedule = self.browser.find_element(By.CSS_SELECTOR, "[class = 'print-nobreak']")

        time.sleep(0.5)

        if flag:
            return schedule.screenshot_as_png
        else:
            return 0

    # получение расписания в виде json
    def get_changes(self, date, built):
        changes = {}
        params = (
            ('__func', 'getSubstViewerDayDataHtml'),
        )

        data = '{"__args":[null,{"date":"' + date + '","mode":"classes"}],"__gsh":"00000000"}'

        r = requests.post(self.way[built], headers=self.headers, params=params, data=data)
        soup = BeautifulSoup(r.text, "lxml")
        changesList = [item.text for item in soup.find_all("span")]
        if "Для этого дня замен нет." in changesList:
            return "Для этого дня замен нет."
        for item in changesList:
            if not (re.search(r"^\d+(\w)( )?/(\w)$", item, flags=re.MULTILINE) is None):
                grade = item
                changes[grade] = {}
            elif (not (re.search(r"^\d?(.) - \d?(.)$", item, flags=re.MULTILINE) is None)
                  or not (re.search(r"^\d?(.)$", item, flags=re.MULTILINE) is None)
                  or not (re.search(r"^\(\d?(.) - \d?(.)\)$", item, flags=re.MULTILINE) is None)
                  or not (re.search(r"^\(\d?(.)\)$", item, flags=re.MULTILINE) is None)):
                lessonNumber = item
            else:
                change = item
                changes[grade][lessonNumber] = change
        return changes
