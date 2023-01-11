from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time

# получение изображения с расписанием с помощью данных о пользователе
def get_schedule(user):
    # установка скрытого режима браузера
    options = webdriver.ChromeOptions()
    options.headless = True

    # открытие браузера
    s = Service("chromedriver.exe")
    browser = webdriver.Chrome(service=s, options=options)
    browser.set_window_size(2100,1100)

    # установка задержки
    wait = WebDriverWait(browser, 20)

    # подключение к сайту
    browser.get("https://gim5cheb.edupage.org/timetable/")

    # открытие меню выбора пользователя
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, f"[title='{ {'student': 'Учащиеся', 'teacher': 'Учителя'}[user.role] }']")))
    browser.find_element(By.CSS_SELECTOR, f"[title='{ {'student': 'Учащиеся', 'teacher': 'Учителя'}[user.role] }']").click()

    wait.until(EC.element_to_be_clickable(
        browser.find_element(By.CSS_SELECTOR, "[class = 'dropDownPanel asc-context-menu'] li")))
    tag = browser.find_element(By.CSS_SELECTOR, "[class = 'dropDownPanel asc-context-menu']")

    clas_found = False
    if user.role == "student":
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class = 'submenu']")))
        if user.grade > 9:
            for clas in tag.find_elements(By.CSS_SELECTOR, "[class = 'submenu']"):
                if clas.text == f"{user.grade}/{user.built}":
                    tag = clas
                    tag.click()
                    clas_found = True
                    break
        else:
            for clas in tag.find_elements(By.CSS_SELECTOR, "[class = 'submenu']"):
                if clas.text == f"{user.grade}{user.symbol}/{user.built}":
                    tag = clas
                    tag.click()
                    clas_found = True
                    break
        if not clas_found:
            return None

    person_found = False
    for person in tag.find_elements(By.CSS_SELECTOR, "[class = 'dropDownPanel asc-context-menu'] li"):
        if f"{user.surname} {user.name}" in person.text:
            person.click()
            person_found = True
            break
    if not person_found:
        return None

    # изменение размеров расписания
    attr1 = browser.find_element(By.CSS_SELECTOR, "[id = 'skin_Container_7']")
    browser.execute_script("arguments[0].style.maxWidth = '4000px';", attr1)

    attr2 = browser.find_element(By.XPATH, "//div[@class='skgd']/div/div[1]")
    browser.execute_script("arguments[0].style.height = '4000px';", attr2)

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class = 'print-nobreak']")))
    schedule = browser.find_element(By.XPATH, "//div[@class='print-nobreak']/div")


    wait.until(
        EC.invisibility_of_element(browser.find_element(By.CSS_SELECTOR, "[class = 'dropDownPanel asc-context-menu']")))

    #сохранение изображения
    Screen = lambda x: browser.execute_script("return document.body.parentNode.scroll" + x)
    browser.set_window_size(2100+44, Screen('Height'))

    return schedule.screenshot_as_png


# a = get_schedule(["Милана", "Сандимирова", 8, "Ю", "А", "student"], 100)
#
# with open("schedule.png", "wb") as file:
#     file.write(a)
#
# get_screenshot()