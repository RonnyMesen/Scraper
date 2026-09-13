from playwright.sync_api import sync_playwright
import time

def test_adobe():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.adobecar.com/en", timeout=60000)
        page.wait_for_load_state("networkidle")
        
        # Click the location dropdown
        page.click(".button-pick.pick-up-place")
        time.sleep(1)
        
        # See what options are available
        titles = page.eval_on_selector_all(".pickup-wrapper .place-title", "nodes => nodes.map(n => n.innerText)")
        print("Available pickup places:", titles)
        
        if titles:
            # Click the first one or San Jose
            target = "San Jose - International Airport SJO" if "San Jose - International Airport SJO" in titles else titles[0]
            print(f"Clicking: {target}")
            page.click(f".pickup-wrapper .place-title:has-text('{target}')")
        
        # Dates are set automatically, click search
        page.click("button.btn-search")
        
        try:
            page.wait_for_selector(".box-results", timeout=15000)
            cars = page.eval_on_selector_all(".box-results .title-car", "nodes => nodes.map(n => n.innerText)")
            print("Cars:", cars)
        except Exception as e:
            print("Could not find results:", e)
            print("HTML Dump:", page.content()[:2000])

        browser.close()

if __name__ == "__main__":
    test_adobe()
