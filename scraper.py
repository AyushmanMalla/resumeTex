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

            # Strip out footers, headers, buttons, and irrelevant blocks cleanly from the DOM
            page.evaluate("""
                document.querySelectorAll('button, [role="button"], a.btn, footer, nav, header, aside, form, svg').forEach(el => el.remove());
            """)

            # Use simple extraction
            raw_text = page.locator("body").inner_text()
            browser.close()
            
            if not raw_text:
                return ""
                
            # Aggressively filter out lines/chunks containing irrelevant boilerplate
            bad_phrases = [
                'cookie', 'equal opportunity', 'equal employment', 'benefits', 
                'social media', 'twitter', 'facebook', 'linkedin', 'instagram',
                'veteran status', 'sexual orientation', 'gender identity', 'national origin'
            ]
            
            clean_lines = []
            for line in raw_text.split('\n'):
                line_lower = line.strip().lower()
                if not line_lower:
                    continue
                if any(phrase in line_lower for phrase in bad_phrases):
                    continue
                clean_lines.append(line)
                
            text = "\n".join(clean_lines)

            if text:
                logging.info("Extraction and filtering successful with Playwright.")
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
