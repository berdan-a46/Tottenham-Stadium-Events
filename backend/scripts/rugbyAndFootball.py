# backend/scripts/rugbyAndFootball.py
from __future__ import annotations

import os
import time
from typing import List, Tuple, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# Optional on local; in container we’ll prefer system chromedriver.
try:
    from webdriver_manager.chrome import ChromeDriverManager  # type: ignore
except Exception:  # pragma: no cover
    ChromeDriverManager = None  # type: ignore

# ---------- Timezone ----------
# Safe tzset (not available on Windows)
try:
    os.environ.setdefault("TZ", "Europe/London")
    import time as _t
    if hasattr(_t, "tzset"):
        _t.tzset()
except Exception:
    pass

from datetime import datetime


# ---------- Config ----------
CHROME_BIN = os.getenv("CHROME_BIN", "/usr/bin/chromium")
CHROMEDRIVER = os.getenv("CHROMEDRIVER", "/usr/bin/chromedriver")

MEN_FIXTURES_URL = os.getenv("MEN_FIXTURES_URL", "https://www.tottenhamhotspur.com/fixtures/men/")
STADIUM_EVENTS_URL = os.getenv("STADIUM_EVENTS_URL", "https://www.tottenhamhotspurstadium.com/whats-on/events-calendar/")

WAIT_SECS = int(os.getenv("SEL_WAIT_SECS", "25"))       # main waits
PAGELOAD_TIMEOUT = int(os.getenv("PAGELOAD_TIMEOUT", "20"))
SCRIPT_TIMEOUT = int(os.getenv("SCRIPT_TIMEOUT", "20"))


# ---------- Helpers ----------
def _make_driver() -> webdriver.Chrome:
    """
    Create a Chrome driver that works on Render (headless, no-sandbox).
    If startup fails, let Selenium raise (you want a 500).
    """
    opts = Options()
    opts.page_load_strategy = "eager"
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-features=NetworkService,NetworkServiceInProcess")
    opts.add_argument("--no-zygote")
    opts.add_argument("--window-size=1280,800")
    opts.add_argument("--lang=en-GB")
    # A realistic UA can help some sites
    opts.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/119.0.0.0 Safari/537.36'
    )
    # Binary location for container
    opts.binary_location = CHROME_BIN

    # Prefer system chromedriver in the container; fall back to webdriver-manager locally
    service = None
    if CHROMEDRIVER and os.path.exists(CHROMEDRIVER):
        service = Service(CHROMEDRIVER)
    elif ChromeDriverManager is not None:
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=opts) if service else webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(PAGELOAD_TIMEOUT)
    driver.set_script_timeout(SCRIPT_TIMEOUT)
    return driver


def _maybe_click_cookie(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    """Dismiss OneTrust cookie banner if present; ignore if not found."""
    try:
        btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        btn.click()
        # allow banner to collapse
        time.sleep(0.25)
    except Exception:
        pass


def formatDateTime(date_fragment: str, day_name: str) -> tuple[str | None, str | None]:
    """
    Your original formatter.
    Input examples:
      date_fragment: "02 AUG, 7:30PM"
      day_name: "Saturday"
    Output date_str matches "%A %d %B %Y", time_str matches "%H:%M"
    """
    months = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
        "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
    }
    try:
        dayNumberAndMonth, time_part = [s.strip() for s in date_fragment.split(",", 1)]
        dayNumber_str, monthStr = dayNumberAndMonth.split()
        dayNumber = int(dayNumber_str)
        month = months[monthStr.upper()]
        # Season crossing assumption preserved:
        year = 2025 if month >= 6 else 2026
        # Build full date
        month_name = datetime(year, month, dayNumber).strftime("%B")
        formattedDate = f"{day_name} {dayNumber:02d} {month_name} {year}"
        # time like "7:30PM" -> "19:30"
        time_24h = datetime.strptime(time_part.replace(".", ":"), "%I:%M%p").strftime("%H:%M")
        return formattedDate, time_24h
    except Exception as e:
        print(f"[formatDateTime] error: {e} | inputs: date_fragment={date_fragment!r}, day_name={day_name!r}")
        return None, None


# ---------- Main scraper ----------
def rugbyAndFootball() -> Tuple[List[list[Any]], List[list[Any]]]:
    """
    Scrape:
      - Stadium events calendar (Rugby)  -> finalRugbyEvents
      - Spurs men fixtures               -> finalEvents (football)

    Return (finalEvents, finalRugbyEvents)
    Each event: [title_or_type, match_or_title, date_str, time_str, optional]
    """
    driver: webdriver.Chrome | None = None
    try:
        driver = _make_driver()
        wait = WebDriverWait(driver, WAIT_SECS)

        # -------------------- Stadium (Rugby) --------------------
        driver.get(STADIUM_EVENTS_URL)
        _maybe_click_cookie(driver, wait)

        # Open filters and select "Rugby"
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "filtersToggle"))).click()
            # The drop-down can be dynamically rendered; wait for it
            eventTypeEl = wait.until(EC.presence_of_element_located((By.ID, "eventType")))
            Select(eventTypeEl).select_by_visible_text("Rugby")
            # Give the grid a moment to refresh
            time.sleep(0.8)
        except TimeoutException:
            # If the filter UI changed, we still want to fail loudly
            raise

        # Grab card links first to avoid stale references after navigation
        rugby_links: list[tuple[str, str]] = []  # (title, href)
        cards = driver.find_elements(
            By.CSS_SELECTOR,
            ".c-grid__col.c-grid__col--4-wide:not(.c-feature-card__container--hidden):not(footer *)"
        )
        for card in cards:
            try:
                title = card.find_element(By.CLASS_NAME, "c-feature-card__title").text.strip()
                link_el = card.find_element(By.XPATH, ".//a[contains(@class,'c-feature-card__link')]")
                href = link_el.get_attribute("href") or ""
                if href:
                    rugby_links.append((title, href))
            except (NoSuchElementException, StaleElementReferenceException):
                continue

        finalRugbyEvents: List[list[Any]] = []
        for title, href in rugby_links:
            # Visit details page to get accurate date/time from "Key Details"
            driver.get(href)
            # Some pages lazy-load; wait for Key Details
            h2 = wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(., 'Key Details')]")))
            container = h2.find_element(By.XPATH, "./..")
            ps = container.find_elements(By.TAG_NAME, "p")
            if len(ps) < 3:
                # Structure changed; fail loudly
                raise RuntimeError(f"Unexpected Key Details structure at {href}")
            timeAndDate = ps[2].text  # e.g. "7:30PM, 02 AUG"
            # Split into time first, then date fragment
            # Your earlier code used the inverse; the content can vary so normalize:
            if "," in timeAndDate and timeAndDate.index(",") > 0:
                left, right = [s.strip() for s in timeAndDate.split(",", 1)]
                # Decide which looks like time (has AM/PM)
                if "AM" in left.upper() or "PM" in left.upper():
                    time_part, date_fragment = left, right
                else:
                    date_fragment, time_part = left, right
                # We also need the day name: often on the page elsewhere; fallback "Saturday"
                # If a day label exists near the card, you can fetch it. For now, assume day name exists on breadcrumb; fallback:
                day_name = "Saturday"
            else:
                # Fallback: single field, try to parse e.g. "Saturday 02 AUG 7:30PM"
                parts = timeAndDate.split()
                day_name = parts[0] if parts else "Saturday"
                # Try to reconstruct "02 AUG, 7:30PM"
                date_fragment = ""
                time_part = ""
                # Find something like "NN MMM"
                for i in range(len(parts) - 1):
                    if parts[i].isdigit() and len(parts[i]) in (1, 2) and parts[i + 1].isalpha() and len(parts[i + 1]) == 3:
                        date_fragment = f"{int(parts[i]):02d} {parts[i+1].upper()}"
                        break
                for p in parts:
                    if "AM" in p.upper() or "PM" in p.upper():
                        time_part = p
                        break
                if date_fragment and time_part:
                    timeAndDate = f"{time_part}, {date_fragment}"
                else:
                    raise RuntimeError(f"Could not parse time/date on {href}: {timeAndDate!r}")

            # Use your formatter
            formattedDate, formattedTime = formatDateTime(f"{date_fragment}, {time_part}", day_name)
            if not (formattedDate and formattedTime):
                raise RuntimeError(f"formatDateTime failed for {timeAndDate!r} at {href}")

            # Stadium name constant for these events
            venue = "Tottenham Hotspur Stadium"
            finalRugbyEvents.append(["rugby", title, formattedDate, formattedTime, href])

        # -------------------- Men’s Fixtures (Football) --------------------
        driver.get(MEN_FIXTURES_URL)
        driver.refresh()  # as per your original flow
        _maybe_click_cookie(driver, wait)

        # Groups and items
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "FixtureGroup")))
        fixtureGroups = driver.find_elements(By.CLASS_NAME, "FixtureGroup")

        finalEvents: List[list[Any]] = []
        for group in fixtureGroups:
            # original had "FixtureItem " (with space); match robustly via CSS:
            fixtures = group.find_elements(By.CSS_SELECTOR, ".FixtureItem")
            for fixture in fixtures:
                try:
                    match_title = fixture.get_attribute("title") or ""

                    # Skip if already played: scores text != "VS"
                    try:
                        scoresText = fixture.find_element(By.CLASS_NAME, "scores").get_attribute("innerHTML").strip()
                    except NoSuchElementException:
                        scoresText = ""
                    if scoresText != "VS":
                        continue

                    fixtureDesktop = fixture.find_element(By.CLASS_NAME, "FixtureItem__desktop")
                    wrapper = fixtureDesktop.find_element(By.CLASS_NAME, "wrapper")

                    # Ensure it's a home game (Tottenham Hotspur Stadium)
                    try:
                        wrapper.find_element(By.CSS_SELECTOR, ".stadium-tag.stadium-tag--home")
                    except NoSuchElementException:
                        continue

                    # Day + date/time block
                    kickoff = wrapper.find_element(By.CLASS_NAME, "FixtureItem__kickoff")
                    fixtureDay = kickoff.find_element(By.TAG_NAME, "p").text.strip()  # e.g., "Saturday"
                    lines = [l.strip() for l in kickoff.text.splitlines() if l.strip()]
                    # You had lines[1] -> date fragment like "02 AUG, 7:30PM"
                    date_fragment = lines[1] if len(lines) > 1 else ""
                    formattedDate, formattedTime = formatDateTime(date_fragment, fixtureDay)
                    if not (formattedDate and formattedTime):
                        continue

                    # Abbreviations list (e.g., ["TOT", "BOU"])
                    abbreviationsAsText: list[str] = []
                    try:
                        crest_ps = wrapper.find_element(By.CLASS_NAME, "FixtureItem__crests").find_elements(By.TAG_NAME, "p")
                        abbreviationsAsText = [p.text.strip() for p in crest_ps if p.text.strip()]
                    except NoSuchElementException:
                        pass

                    finalEvents.append(["Football", match_title, formattedDate, formattedTime, abbreviationsAsText])

                except Exception:
                    # Keep failing loud for startup errors, but individual malformed items can be skipped
                    continue

        return finalEvents, finalRugbyEvents

    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
