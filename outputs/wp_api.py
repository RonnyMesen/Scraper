import requests
import logging
import json

logger = logging.getLogger(__name__)

class WordPressAPIOutput:
    def __init__(self, endpoint_url="https://costaricatransit.com/wp-json/crt/v1/ingest", api_secret="YOUR_API_SECRET_HERE"):
        self.endpoint_url = endpoint_url
        self.api_secret = api_secret

    def save_data(self, scraped_data):
        if not scraped_data:
            logger.warning("No data to send to WordPress API")
            return False

        headers = {
            'Content-Type': 'application/json',
            'x-crt-token': 'crt_scraper_super_secret_2026'
        }

        try:
            # We are sending the JSON payload just like we did in the POC
            response = requests.post(self.endpoint_url, json=scraped_data, headers=headers)
            if response.status_code == 200:
                logger.info(f"Successfully synced with WordPress API. Response: {response.text}")
                return True
            else:
                logger.error(f"Failed to sync with WordPress API. Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exception during WordPress API sync: {e}")
            return False
