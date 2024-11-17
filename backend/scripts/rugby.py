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
    finalEvents = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = os.getenv("CHROME_BINARY_PATH", "/usr/bin/google-chrome")

    try:
        print("Setting up WebDriver")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        print("Navigating to the website")
        driver.get('https://www.tottenhamhotspurstadium.com/whats-on/events-calendar/')
        
        wait = WebDriverWait(driver, 10)

        print("Waiting for cookies banner and filters toggle to load")
        wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))).click()
        wait.until(EC.element_to_be_clickable((By.ID, 'filtersToggle'))).click()

        print("Locating event type dropdown")
        eventTypeDropdown = Select(driver.find_element(By.ID, 'eventType'))
        eventTypeDropdown.select_by_visible_text('Rugby')
        
        print("Fetching rugby events")
        rugbyEvents = driver.find_elements(By.CSS_SELECTOR, ".c-grid__col.c-grid__col--4-wide:not(.c-feature-card__container--hidden):not(footer *)")
        print(f"Number of events found: {len(rugbyEvents)}")

        for event in rugbyEvents:
            try:
                title = event.find_element(By.CLASS_NAME, 'c-feature-card__title').text
                date = event.find_element(By.CLASS_NAME, 'c-feature-card__text').text
                
                print(f"Event found: Title = {title}, Date = {date}")
                
                linkElement = event.find_element(By.XPATH, ".//a[@class='c-feature-card__link']")
                hrefLink = linkElement.get_attribute("href")
                
                print(f"Navigating to event details: {hrefLink}")
                driver.get(hrefLink)

                keyDetailsWithWait = wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Key Details')]")))
                parentDiv = keyDetailsWithWait.find_element(By.XPATH, "./..")
                timeAndDate = parentDiv.find_elements(By.TAG_NAME, "p")[2].text
                print(f"Raw time and date: {timeAndDate}")

                timeString = timeAndDate.split(",")[0].replace('.', ':')
                timeString24H = datetime.strptime(timeString, "%I:%M%p").strftime("%H:%M")
                print(f"Formatted time: {timeString24H}")

                arrayToAppend = ["rugby", title, date, timeString24H]
                finalEvents.append(arrayToAppend)

            except Exception as e:
                print(f"Error processing event: {e}")
                pass

    except Exception as e:
        print(f"Error during rugby scraping: {e}")

    finally:
        print("Quitting WebDriver")
        driver.quit()

    print(f"Final events: {finalEvents}")
    return finalEvents
