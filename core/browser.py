import time
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

class StealthBrowser:
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()
        # Use chromium with stealth args
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process"
        ]
        self.browser = self.playwright.chromium.launch(headless=self.headless, args=args)
        
        # Create context with realistic viewport and user agent
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="es-CR",
            timezone_id="America/Costa_Rica"
        )
        self.page = self.context.new_page()
        
        # Apply stealth plugin to mask Playwright
        stealth_sync(self.page)
        return self.page

    def stop(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def human_delay(self, min_sec=1.5, max_sec=4.0):
        """Simulate human reading/thinking time."""
        time.sleep(random.uniform(min_sec, max_sec))

    def human_scroll(self, scroll_steps=3):
        """Simulate a human scrolling down the page."""
        for _ in range(scroll_steps):
            self.page.mouse.wheel(0, random.randint(300, 700))
            self.human_delay(0.5, 1.5)
