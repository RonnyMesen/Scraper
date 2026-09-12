import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GoogleDriveOutput:
    def __init__(self, credentials_file='credentials.json', spreadsheet_name='CostaRicaTransit_ScrapedData'):
        self.credentials_file = credentials_file
        self.spreadsheet_name = spreadsheet_name
        self.client = None
        self.sheet = None
        self._authenticate()

    def _authenticate(self):
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
            self.client = gspread.authorize(creds)
            # Try to open, if it fails because it doesn't exist, we assume the user created it manually and shared it.
            # In a production environment, you might create it dynamically if it doesn't exist.
            self.sheet = self.client.open(self.spreadsheet_name).sheet1
        except Exception as e:
            logger.error(f"Google Drive Authentication Failed: {e}")
            logger.warning("Make sure credentials.json exists and the spreadsheet is shared with the service account email.")

    def save_data(self, scraped_data):
        if not self.sheet:
            logger.error("No Google Sheet connected. Cannot save data.")
            return False

        # If sheet is empty, write headers
        try:
            headers = self.sheet.row_values(1)
            if not headers:
                self.sheet.append_row([
                    "Timestamp (UTC)", "Provider ID", "Category", "Vehicle Model", 
                    "Currency", "Base Rate", "Mandatory TPL", "Agency CDW", "IVA"
                ])
        except Exception as e:
            logger.error(f"Error checking headers: {e}")

        # Append new rows
        rows_to_insert = []
        for item in scraped_data:
            rows_to_insert.append([
                item.get('timestamp_utc', datetime.utcnow().isoformat() + 'Z'),
                item.get('provider_id', ''),
                item.get('category', ''),
                item.get('vehicle_model', ''),
                item.get('currency', 'USD'),
                item.get('pricing', {}).get('base_rate_per_day', ''),
                item.get('pricing', {}).get('mandatory_tpl_per_day', ''),
                item.get('pricing', {}).get('agency_cdw_per_day', ''),
                item.get('pricing', {}).get('iva_percentage', '')
            ])
            
        if rows_to_insert:
            try:
                self.sheet.append_rows(rows_to_insert)
                logger.info(f"Successfully saved {len(rows_to_insert)} rows to Google Sheets.")
                return True
            except Exception as e:
                logger.error(f"Failed to append rows to Google Sheets: {e}")
                return False
        return True
