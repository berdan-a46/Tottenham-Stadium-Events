# backend/scripts/rugby.py
from __future__ import annotations

import os
from typing import List, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROME_BIN = os.getenv("CHROME_BIN", "/usr/bin/chromium")
CHROMEDRIVER = os.getenv("CHROMEDRIVER", "/usr/bin/chromedriver")

def _make_driver() -> webdriver.Chrome:
    """
    Create a Chrome driver that works on Render.
    If Chrome/driver can't start, raise the Selenium exception (do NOT catch).
    """
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,800")
    opts.binary_location = CHROME_BIN

    # Prefer system chromedriver if present; otherwise let Selenium Manager find one
    service = None
    for path in (CHROMEDRIVER, "/usr/lib/chromium/chromedriver", "/usr/bin/chromedriver"):
        if os.path.exists(path):
            service = Service(path)
            break

    if service:
        return webdriver.Chrome(service=service, options=opts)
    else:
        # Selenium Manager will download/resolve a compatible driver.
        # If that fails, the exception will bubble up — exactly as desired.
        return webdriver.Chrome(options=opts)

def rugby() -> List[list[Any]]:
    """
    Scrape and return events as:
        [title, venue, date_str, time_str, optional_url]
    Any Selenium failure should raise, producing a 500 in Django.
    """
    driver = None
    try:
        driver = _make_driver()

        # TODO: replace with your real URL + selectors
        url = "https://example.com/rugby"
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".event-card, .event-item")))

        events: List[list[Any]] = []
        cards = driver.find_elements(By.CSS_SELECTOR, ".event-card, .event-item")
        for c in cards:
            title = c.find_element(By.CSS_SELECTOR, ".event-title").text.strip()
            date_str = c.find_element(By.CSS_SELECTOR, ".event-date").text.strip()
            time_str = c.find_element(By.CSS_SELECTOR, ".event-time").text.strip()
            venue = ""
            try:
                venue = c.find_element(By.CSS_SELECTOR, ".event-venue").text.strip()
            except Exception:
                venue = "Tottenham Hotspur Stadium"
            link = ""
            try:
                link = c.find_element(By.CSS_SELECTOR, "a").get_attribute("href") or ""
            except Exception:
                pass
            events.append([title, venue, date_str, time_str, link])

        return events

    finally:
        # IMPORTANT: never assume driver exists
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                # We still want the original exception (if any) to surface,
                # so we deliberately ignore errors during quit().
                pass
