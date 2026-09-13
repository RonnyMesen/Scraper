import logging
import time
import json
import html
import requests
import urllib.parse
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AdobeScraper:
    def __init__(self, browser_manager=None, start_date=None, end_date=None):
        self.browser_manager = browser_manager
        
        if not start_date:
            now = datetime.now()
            start_date_obj = now + timedelta(days=1)
            self.start_date = start_date_obj.strftime("%Y-%m-%d")
        else:
            self.start_date = start_date
            
        if not end_date:
            now = datetime.now()
            end_date_obj = now + timedelta(days=8)
            self.end_date = end_date_obj.strftime("%Y-%m-%d")
        else:
            self.end_date = end_date

    def scrape(self):
        logger.info(f"Starting API scrape for Adobe Rent a Car: {self.start_date} to {self.end_date}")
        results = []

        try:
            url = 'https://www.adobecar.com/wp-admin/admin-ajax.php'
            
            # Using OCO which is Adobe's internal code for SJO Airport
            query = {
                'adobe_search': '1', 
                'pick_up_place': 'OCO', 
                'drop_off_place': 'OCO', 
                'pick_up_date': self.start_date, 
                'drop_off_date': self.end_date, 
                'pick_up_time': '08:00:00', 
                'drop_off_time': '08:00:00', 
                'cr_resident': '2'
            }
            
            params = '?' + urllib.parse.urlencode(query)
            payload = {
                'action': 'adobe_renting_search_result', 
                'url_search': params
            }
            
            logger.info("Sending POST request to Adobe API...")
            r = requests.post(url, data=payload, headers={'User-Agent': 'Mozilla/5.0'})
            r.raise_for_status()
            
            data = r.json()
            if 'adobe_search_result' not in data:
                logger.error("Unexpected response format from Adobe API")
                return results
                
            html_content = data['adobe_search_result'].get('div.result_container', '')
            if 'No hay resultados' in html_content:
                logger.warning("Adobe API returned 'No hay resultados' (No inventory for these dates).")
                return results
                
            soup = BeautifulSoup(html_content, 'html.parser')
            input_val = soup.select_one('input.response-adobe')
            
            if not input_val or not input_val.get('value'):
                logger.error("Could not find input.response-adobe in API response")
                return results
                
            cars = json.loads(html.unescape(input_val['value']))
            logger.info(f"Successfully extracted {len(cars)} cars from Adobe API.")
            
            for car in cars:
                dias = car.get('dias', 1)
                precio_total = car.get('precio', 0)
                seguro_basico = car.get('seguroBasico', 0)
                
                base_rate = round(precio_total / dias, 2) if dias > 0 else precio_total
                
                results.append({
                    "provider_id": "adobe_cr",
                    "category": car.get('tipo', 'UNKNOWN'),
                    "vehicle_model": car.get('modelo', 'Unknown Model'),
                    "currency": "USD",
                    "pricing": {
                        "base_rate_per_day": base_rate,
                        "mandatory_tpl_per_day": seguro_basico,
                        "agency_cdw_per_day": 0,
                        "iva_percentage": 0.13
                    }
                })
                
        except Exception as e:
            logger.error(f"Error scraping Adobe via API: {e}")
            
        return results
