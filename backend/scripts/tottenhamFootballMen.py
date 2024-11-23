from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import os

os.environ['TZ'] = 'Europe/London'
time.tzset()

def formatDateTime(date, day):
    months = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
        "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
    }
    try:
        dayNumberAndMonth, time = date.split(",")
        dayNumber, monthStr = dayNumberAndMonth.split()
        dayNumber = int(dayNumber)
        month = months[monthStr]
        year = 2024 if month >= 6 else 2025
        formattedDate = f"{day} {dayNumber:02d} {datetime(year, month, dayNumber).strftime('%B')} {year}"
        formattedTime = time
        return formattedDate, formattedTime
    
    except Exception as e:
        print(f"Error in format_date_time: {e}")
        return None, None


def tottenhamFootballMen():
    finalEvents = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = os.getenv("CHROME_BINARY_PATH", "/usr/bin/google-chrome")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://www.tottenhamhotspur.com/fixtures/men/')
    driver.refresh()
    
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler'))).click()

    fixtureGroups = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME,"FixtureGroup")))
    for group in fixtureGroups:
        fixtureItems = group.find_elements(By.CLASS_NAME, "FixtureItem ")
        for fixture in fixtureItems:
            match = fixture.get_attribute("title")

            #Figure out if it's been played or not
            scoresText = fixture.find_element(By.CLASS_NAME,"scores").get_attribute("innerHTML")
            if scoresText != "VS":
                continue
            try:
                fixtureDesktop = fixture.find_element(By.CLASS_NAME, 'FixtureItem__desktop')
                fixtureDesktopWrapper = fixtureDesktop.find_element(By.CLASS_NAME, 'wrapper')
                homeGameTest = fixtureDesktopWrapper.find_element(By.CSS_SELECTOR, '.stadium-tag.stadium-tag--home')
                fixtureItemKickOffTime = fixtureDesktopWrapper.find_element(By.CLASS_NAME, 'FixtureItem__kickoff')
                fixtureDay = fixtureItemKickOffTime.find_element(By.TAG_NAME, 'p').text
                fixtureItemKickOffTimeText = fixtureItemKickOffTime.text
                fixtureDate = fixtureItemKickOffTimeText.splitlines()[1]
                formattedDate, formattedTime = formatDateTime(fixtureDate, fixtureDay)
                
                abbreviationsAsText = []
                abbreviations = fixtureDesktopWrapper.find_element(By.CLASS_NAME, 'FixtureItem__crests').find_elements(By.TAG_NAME, "p")
                for abbreviation in abbreviations:
                    abbreviationsAsText.append(abbreviation.text)

                arrayToAppend = ["Football",match, formattedDate, formattedTime,abbreviationsAsText]
                finalEvents.append(arrayToAppend)
            except Exception as e:
                pass

    driver.quit()
    return finalEvents

