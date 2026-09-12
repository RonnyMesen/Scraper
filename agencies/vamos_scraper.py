import logging
import time
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from core.browser import get_browser_context

logger = logging.getLogger(__name__)

def build_vamos_url(start_date: str, end_date: str, pickup: str, dropoff: str) -> str:
    """
    Constructs the direct reservation URL for Vamos Rent-A-Car.
    Uses '1' for SJO Airport location.
    Format of date required by Vamos: YYYYMMDD
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        fecha_inicio_r2 = start_dt.strftime("%Y%m%d")
        fecha_final_r2 = end_dt.strftime("%Y%m%d")
    except ValueError:
        fecha_inicio_r2 = start_date.replace("-", "")
        fecha_final_r2 = end_date.replace("-", "")
        
    pickuplocation_v = "1" if pickup.upper() == "SJO" else "2"
    dropLocation_v = "1" if dropoff.upper() == "SJO" else "2"
    timeIni = "0600AM"
    timeFin = "0600AM"
    
    url = "https://reservations.vamosrentacar.com/Search/StepSearch/VAMOS|EN|"
    url += f"{fecha_inicio_r2}|{pickuplocation_v}|{timeIni}|"
    url += f"{fecha_final_r2}|{dropLocation_v}|{timeFin}|VamosSite|H"
    return url

async def fetch_vamos_data(start_date, end_date, pickup, dropoff):
    """
    Fetches actual pricing data from Vamos Rent-A-Car using Playwright.
    """
    logger.info("Starting scrape for Vamos Rent-A-Car")
    
    url = build_vamos_url(start_date, end_date, pickup, dropoff)
    logger.info(f"Navigating to Vamos direct URL...")
    
    html_content = ""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            page = await context.new_page()
            
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            logger.info("Waiting for results to load...")
            try:
                await page.wait_for_selector(".price-box, .carnotavailable", timeout=20000)
            except Exception as e:
                logger.warning(f"Timeout waiting for results on Vamos: {e}")
                
            html_content = await page.content()
            logger.info(f"Loaded Vamos results. HTML size: {len(html_content)} bytes")
            
            try:
                await page.screenshot(path="vamos_debug.png")
                with open("vamos_debug.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
            except Exception as e:
                logger.warning(f"Failed to save debug artifacts: {e}")

        except Exception as e:
            logger.error(f"Error scraping Vamos: {str(e)}")
            return []
        finally:
            await browser.close()
            
    logger.info("Parsing Vamos results...")
    soup = BeautifulSoup(html_content, 'html.parser')
    vehicles = []
    
    for card in soup.find_all('div', class_='vehicule'):
        try:
            name_elem = card.find('p', class_='text-center')
            name = name_elem.text.strip().replace('\n', ' ').strip() if name_elem else "Unknown Vehicle"
            name = " ".join(name.split())
            
            price_elem = card.find('div', class_='right-price')
            is_sold_out = 'carnotavailable' in card.get('class', [])
            
            if is_sold_out or not price_elem:
                continue
                
            price_text = price_elem.text.strip().replace('$', '').replace(',', '')
            price = float(price_text)
            
            vehicles.append({
                "agency": "Vamos",
                "name": name,
                "price": price,
                "currency": "USD"
            })
            
        except Exception as e:
            logger.warning(f"Error parsing a vehicle card on Vamos: {e}")
            
    logger.info(f"Successfully scraped {len(vehicles)} vehicles from Vamos.")
    return vehicles

class VamosScraper:
    def __init__(self, browser_manager=None, start_date="2026-09-20", end_date="2026-09-27", pickup="SJO", dropoff="SJO"):
        self.browser_manager = browser_manager
        self.start_date = start_date
        self.end_date = end_date
        self.pickup = pickup
        self.dropoff = dropoff

    def scrape(self):
        return asyncio.run(fetch_vamos_data(self.start_date, self.end_date, self.pickup, self.dropoff))
