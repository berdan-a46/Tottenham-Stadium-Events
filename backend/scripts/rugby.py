from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime

import os

def rugby():
    finalEvents =[]
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = os.getenv("CHROME_BINARY_PATH", "/usr/bin/google-chrome")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://www.tottenhamhotspurstadium.com/whats-on/events-calendar/') 
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))).click()
    wait.until(EC.element_to_be_clickable((By.ID, 'filtersToggle'))).click()


    eventTypeDropdown = Select(driver.find_element(By.ID, 'eventType'))

    eventTypeDropdown.select_by_visible_text('Rugby')
    rugbyEvents = driver.find_elements(By.CSS_SELECTOR, ".c-grid__col.c-grid__col--4-wide:not(.c-feature-card__container--hidden):not(footer *)")

    for event in rugbyEvents:
        try:
            title = event.find_element(By.CLASS_NAME, 'c-feature-card__title').text
            date = event.find_element(By.CLASS_NAME, 'c-feature-card__text').text
            
            linkElement = event.find_element(By.XPATH, ".//a[@class='c-feature-card__link']")
            hrefLink = linkElement.get_attribute("href")

            driver.get(hrefLink)
            keyDetailsWithWait = wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Key Details')]")))

            parentDiv = keyDetailsWithWait.find_element(By.XPATH,"./..")
            timeAndDate = parentDiv.find_elements(By.TAG_NAME,"p")[2].text
            timeString = timeAndDate.split(",")[0].replace('.', ':')
            timeString24H = datetime.strptime(timeString, "%I:%M%p").strftime("%H:%M")
            arrayToAppend = ["rugby",title, date, timeString24H]
            finalEvents.append(arrayToAppend)

        except Exception as e:
            print("Exception", e)
            pass

    driver.quit()
    return finalEvents

