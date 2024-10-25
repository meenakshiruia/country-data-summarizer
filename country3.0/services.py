import logging
from api import fetch_country_data, fetch_economy_data
from database import store_country_data, store_economy_data, get_country_data
from summary import get_country_data_summary

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(country_name):
    # Fetch country data
    country_data = fetch_country_data(country_name)
    
    if country_data:
        logger.info(f"Fetched data for {country_name}: {country_data}")
        
        # Store country data
        store_country_data(country_data)
        
        # Fetch economy data
        economy_data = fetch_economy_data(country_name)
        if economy_data:
            store_economy_data(country_name, economy_data)
        
        # Generate summary
        summary = get_country_data_summary(country_data)
        if summary:
            logger.info(f"Summary for {country_name}: {summary['summary']}")
        else:
            logger.warning(f"No summary generated for {country_name}.")
    else:
        logger.warning(f"No data available for {country_name}.")

if __name__ == "__main__":
    # Example country name (you can replace this with any valid country name)
    main("Canada")
