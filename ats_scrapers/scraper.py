#!/usr/bin/env python3
"""
Robust Job Description Scraper (with Service-based driver init)
----------------------------------------------------------------
Phase 1 scraper that:
  1. Loads pages via Selenium (headless Chrome)
  2. Simulates “Show more” clicks and scrolling to load dynamic content
  3. Attempts to extract the main text via Mozilla Readability
  4. Falls back to density-filtered body text
  5. Falls back to aggregating all <p> paragraphs
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


CHROMEDRIVER_PATH = r"C:\Users\Ayushman\.wdm\drivers\chromedriver\win64\137.0.7151.68\chromedriver-win64\chromedriver.exe"

def setup_driver(headless: bool = True, window_size: str = "1920,1080"):
    if not os.path.exists(CHROMEDRIVER_PATH):
        raise FileNotFoundError(f"ChromeDriver not found at: {CHROMEDRIVER_PATH}")
    
    service = Service(executable_path=CHROMEDRIVER_PATH)
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=" + window_size)

    return webdriver.Chrome(service=service, options=opts)

def click_show_more(driver, pause: float = 1.0):
    try:
        buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show more')"
            " or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'more')]"
        )
        for btn in buttons:
            try:
                btn.click()
                time.sleep(pause)
            except Exception:
                continue
    except Exception:
        pass


def scroll_to_bottom(driver, step: int = 400, pause: float = 0.5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script(f"window.scrollBy(0, {step});")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def readability_extract(driver) -> str:
    try:
        # Inject Readability script (UMD-compatible build)
        with open("readability.min.js", "r", encoding="utf-8") as f:
            readability_js = f.read()
            driver.execute_script(readability_js)

        # Inject DOMPurify to sanitize HTML if you want (optional, but can skip for now)

        # Now run Readability on a cloned document
        script = """
            let article = new Readability(document.cloneNode(true)).parse();
            return article ? article.textContent : "";
        """
        content = driver.execute_script(script)
        return content or ""
    except Exception as e:
        logging.warning(f"Readability extraction failed: {e}")
        return ""

def density_fallback(driver) -> str:
    try:
        full_text = driver.find_element(By.TAG_NAME, "body").text
    except Exception:
        return ""
    blocks = [blk.strip() for blk in full_text.split("\n\n") if blk.strip()]
    dense = [blk for blk in blocks if len(blk.split()) >= 20]
    return "\n\n".join(dense) if dense else ""


def paragraph_fallback(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    paras = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    return "\n\n".join(paras)


def selenium_scrape_job_description(
    url: str,
    timeout: int = 60,
    headless: bool = True
) -> str:
    driver = setup_driver(headless=headless)
    if not driver:
        return ""

    try:
        driver.set_page_load_timeout(timeout)
        logging.info(f"Loading page: {url}")
        driver.get(url)

        time.sleep(2)
        click_show_more(driver)
        scroll_to_bottom(driver)

        # 1) Readability
        text = readability_extract(driver)
        if text:
            logging.info("Readability extraction succeeded")
            return text.strip()

        # 2) Density filter
        text = density_fallback(driver)
        if text:
            logging.info("Density fallback succeeded")
            return text.strip()

        # 3) Paragraph fallback
        html = driver.page_source
        text = paragraph_fallback(html)
        if text:
            logging.info("Paragraph fallback succeeded")
            return text.strip()

        logging.warning("All extraction methods failed; returning empty string")
        return ""
    except TimeoutException:
        logging.error("Page load timed out")
        return ""
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return ""
    finally:
        driver.quit()


if __name__ == "__main__":
    # test_url = "https://jobs.bytedance.com/en/position/7377543090393139507/detail"
    test_url = "https://blackrock.wd1.myworkdayjobs.com/en-US/BlackRock_Professional/job/Vice-President--ServiceNow-Architect_R253208-1"
    jd_text = selenium_scrape_job_description(test_url)
    print("\n--- Job Description Preview ---\n")
    print(jd_text)

# print(generic_scraper("https://blackrock.wd1.myworkdayjobs.com/en-US/BlackRock_Professional/job/Vice-President--ServiceNow-Architect_R253208-1"))