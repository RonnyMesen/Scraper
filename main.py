import logging
from agencies.adobe_scraper import AdobeScraper
from agencies.vamos_scraper import VamosScraper
from outputs.wp_api import WordPressAPIOutput
from outputs.google_drive import GoogleDriveOutput

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CRT_Scraper_Orchestrator")

def main():
    logger.info("Initializing Scraper Pipeline...")
    
    # 1. Initialize outputs
    # WP API (Real Time Syncer)
    wp_output = WordPressAPIOutput(endpoint_url="https://costaricatransit.com/wp-json/crt/v1/ingest")
    
    # Google Drive (Data Warehouse)
    gdrive_output = GoogleDriveOutput(credentials_file='credentials.json', spreadsheet_name='CostaRicaTransit_ScrapedData')
    
    # 2. Extract Data from Agencies
    all_scraped_data = []
    
    logger.info("Starting extraction from Adobe...")
    adobe = AdobeScraper(None)
    all_scraped_data.extend(adobe.scrape())
    
    logger.info("Starting extraction from Vamos...")
    vamos = VamosScraper(None)
    all_scraped_data.extend(vamos.scrape())
    
    # 3. Output Data
    if all_scraped_data:
        logger.info(f"Total vehicles scraped: {len(all_scraped_data)}. Sending to pipelines...")
        
        # A) Update Live Website
        wp_output.save_data(all_scraped_data)
        
        # B) Append to Google Sheets (Data Warehouse)
        gdrive_output.save_data(all_scraped_data)
        
        logger.info("Pipeline execution completed successfully.")
    else:
        logger.warning("No data was extracted from any agency. Pipelines skipped.")

if __name__ == "__main__":
    main()
