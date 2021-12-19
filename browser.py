from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

class WebFunction:

    def __init__(self):
        s = Service("D:\\pythonProjects\\gym5bot\\chromedriver.exe")
        self.browser = webdriver.Chrome(service=s)
        self.browser.set_window_size(1920,1080)

    def get_schedule(self, name, surname, grade, symbol, built):
        self.browser.get("https://gim5cheb.edupage.org/timetable/")
        time.sleep(3)
        self.browser.find_element(By.CSS_SELECTOR, "[title='Учащиеся']").click()
        time.sleep(1)
        if int(grade) > 9:
            for number in self.browser.find_elements(By.CSS_SELECTOR, "[class = 'submenu']"):
                if number.text == f"{grade}/{built}":
                    number.click()
        else:
            for number in self.browser.find_elements(By.CSS_SELECTOR, "[class = 'submenu']"):
                if number.text == f"{grade}{symbol}/{built}":
                    number.click()

        time.sleep(1)
        for student in self.browser.find_elements(By.CSS_SELECTOR, "[class = 'dropDownPanel asc-context-menu'] li"):
            if f"{surname} {name}" in student.text:
                student.click()
        time.sleep(1)
        schedule = self.browser.find_element(By.ID, "skin_PageContent_2")
        path = f"{name}_{surname}_{grade}{symbol}_{built}"
        with open(f"temp_picture\\{path}.png", "wb") as file:
            file.write(schedule.screenshot_as_png)
        return path
