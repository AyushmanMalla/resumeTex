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
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def setup_driver(headless: bool = True, window_size: str = "1920,1080"):
    """Initializes a Selenium WebDriver with automatic driver management."""
    try:
        service = Service(ChromeDriverManager().install())
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=" + window_size)
        return webdriver.Chrome(service=service, options=opts)
    except ValueError as e:
        logging.error(f"WebDriverManager failed. Ensure you have a working internet connection or try installing manually! Error: {e}")
        return None


def click_show_more(driver, timeout: int = 5, pause: float = 1.0):
    """Finds and clicks 'show more' buttons, waiting for them to be clickable."""
    try:
        wait = WebDriverWait(driver, timeout)
        buttons = wait.until(EC.presence_of_all_elements_located((
            By.XPATH,
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show more')"
            " or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'more')]"
        )))
        for btn in buttons:
            try:
                # Scroll button into view and click
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(0.5) # Brief pause for UI to settle
                btn.click()
                logging.info("Clicked a 'show more' button.")
                time.sleep(pause) # Wait for content to load
            except ElementNotInteractableException:
                logging.warning("Button was not interactable, attempting to click with JavaScript.")
                driver.execute_script("arguments[0].click();", btn)
            except Exception as e:
                logging.warning(f"Could not click a button: {e}")
                continue
    except TimeoutException:
        logging.info("No 'show more' buttons found within the timeout period.")
    except Exception as e:
        logging.error(f"An error occurred while trying to click 'show more' buttons: {e}")


def scroll_to_bottom(driver, pause: float = 0.5):
    """Scrolls to the bottom of the page to trigger lazy-loaded content."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    logging.info("Scrolled to the bottom of the page.")


def readability_extract(driver) -> str:
    """Extracts main content using Mozilla's Readability.js."""
    try:
        # Inject Readability.js if not present
        driver.execute_script('''
            if (!window.Readability) {
                let script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/@mozilla/readability@0.4.4/Readability.min.js';
                script.type = 'text/javascript';
                document.head.appendChild(script);
                return new Promise(resolve => script.onload = resolve);
            }
        ''')
        # Wait for script to load
        time.sleep(1)

        # Execute Readability
        content = driver.execute_script('''
            if (window.Readability) {
                let article = new Readability(document.cloneNode(true)).parse();
                return article ? article.textContent : "";
            }
            return "";
        ''')
        return content or ""
    except Exception as e:
        logging.warning(f"Readability.js extraction failed: {e}")
        return ""

def density_fallback(driver) -> str:
    """Fallback extractor based on text density of blocks."""
    try:
        full_text = driver.find_element(By.TAG_NAME, "body").text
    except Exception:
        return ""
    blocks = [blk.strip() for blk in full_text.split("\n\n") if blk.strip()]
    # A simple density filter: blocks with more than 20 words
    dense_blocks = [blk for blk in blocks if len(blk.split()) >= 20]
    return "\n\n".join(dense_blocks) if dense_blocks else ""


def paragraph_fallback(html: str) -> str:
    """Fallback extractor that joins all paragraph tags."""
    soup = BeautifulSoup(html, "lxml")
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    return "\n\n".join(paragraphs)


def selenium_scrape_job_description(
    url: str,
    timeout: int = 30,
    headless: bool = True
) -> str:
    """
    Scrapes the main text content of a job description from a URL.

    Args:
        url: The URL of the job description.
        timeout: Page load timeout in seconds.
        headless: Whether to run the browser in headless mode.

    Returns:
        The extracted job description text, or an empty string on failure.
    """
    driver = setup_driver(headless=headless)
    if not driver:
        return ""

    try:
        driver.set_page_load_timeout(timeout)
        logging.info(f"Loading page: {url}")
        driver.get(url)

        # Allow time for initial page load and dynamic content
        time.sleep(3)

        click_show_more(driver)
        scroll_to_bottom(driver)

        # Attempt extraction strategies
        text = readability_extract(driver)
        if text:
            logging.info("Extraction successful with Readability.js.")
            return text.strip()

        text = density_fallback(driver)
        if text:
            logging.info("Extraction successful with density fallback.")
            return text.strip()

        html = driver.page_source
        text = paragraph_fallback(html)
        if text:
            logging.info("Extraction successful with paragraph fallback.")
            return text.strip()

        logging.warning("All extraction methods failed. No meaningful content found.")
        return ""

    except TimeoutException:
        logging.error(f"Page load timed out after {timeout} seconds for URL: {url}")
        return ""
    except WebDriverException as e:
        logging.error(f"WebDriver error occurred: {e}")
        return ""
    except Exception as e:
        logging.error(f"An unexpected error occurred during scraping: {e}")
        return ""
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Example usage for testing
    test_url = "https://jobs.bytedance.com/en/position/7377543090393139507/detail"
    # test_url = "https://blackrock.wd1.myworkdayjobs.com/en-US/BlackRock_Professional/job/Vice-President--ServiceNow-Architect_R253208-1"
    
    jd_text = selenium_scrape_job_description(test_url, headless=True)
    
    if jd_text:
        print("\n--- Scraped Job Description (Preview) ---")
        print(jd_text[:1500] + "...")
    else:
        print("\n--- Failed to scrape job description ---")
