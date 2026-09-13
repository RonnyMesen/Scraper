from playwright.sync_api import sync_playwright

def get_html_and_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.adobecar.com/en/", timeout=60000)
        
        page.wait_for_load_state("networkidle")
        
        page.screenshot(path="adobe_home.png")
        with open("adobe_home.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        browser.close()

if __name__ == "__main__":
    get_html_and_screenshot()
