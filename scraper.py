import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def playwright_scrape_job_description(url: str, timeout: int = 30000, headless: bool = True) -> str:
    """
    Scrapes the main text content of a job description from a URL using Playwright.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            logging.info(f"Loading page: {url}")
            page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            
            # Simple fallback for show more
            try:
                for button in page.locator("button:has-text('more'), button:has-text('show more')").all():
                    if button.is_visible():
                        button.click()
            except Exception:
                pass
                
            # Scroll down
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)

            # Use simple extraction
            text = page.locator("body").inner_text()
            browser.close()
            
            if text:
                logging.info("Extraction successful with Playwright.")
                return text.strip()
            return ""
    except PlaywrightTimeoutError:
        logging.error(f"Page load timed out for URL: {url}")
        return ""
    except Exception as e:
        logging.error(f"An unexpected error occurred during scraping: {e}")
        return ""

if __name__ == "__main__":
    test_url = "https://jobs.bytedance.com/en/position/7377543090393139507/detail"
    jd_text = playwright_scrape_job_description(test_url, headless=True)
    if jd_text:
        print("\n--- Scraped Job Description (Preview) ---")
        print(jd_text[:1500] + "...")
    else:
        print("\n--- Failed to scrape job description ---")
