import os
import requests
import logging

# Set up logging
logger = logging.getLogger(__name__)

API_KEY = os.getenv('YOUR_API_KEY')

def fetch_country_data(country_name):
    api_url = f"https://api.api-ninjas.com/v1/country?name={country_name}"
    try:
        response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()[0]
            return {
                'country_name': country_name,
                'surface_area': data.get('surface_area', 0),
                'exports': data.get('exports', 0),
                'tourists': data.get('tourists', 0),
                'gdp': data.get('gdp', 0),
                'population': data.get('population', 0),
                'imports': data.get('imports', 0),
                'urban_population_growth': data.get('urban_population_growth', 0),
                'urban_population': data.get('urban_population', 0),
                'gdp_growth': data.get('gdp_growth', 0),
                'gdp_per_capita': data.get('gdp_per_capita', 0)
            }
    except requests.RequestException as e:
        logger.error(f"Error fetching data for {country_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching data for {country_name}: {str(e)}")
    
    return None

def fetch_economy_data(country_name):
    api_url = f"https://api.api-ninjas.com/v1/country?name={country_name}"
    
    try:
        response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                data = data[0]
                return {
                    'imports': data.get('imports', 0),
                    'urban_population_growth': data.get('urban_population_growth', 0),
                    'exports': data.get('exports', 0),
                    'population': data.get('population', 0),
                    'urban_population': data.get('urban_population', 0),
                    'gdp': data.get('gdp', 0),
                    'gdp_growth': data.get('gdp_growth', 0),
                    'gdp_per_capita': data.get('gdp_per_capita', 0)
                }
            else:
                logger.warning(f"No data returned for {country_name}")
                return None
    except requests.RequestException as e:
        logger.error(f"Error fetching data for {country_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching data for {country_name}: {str(e)}")
    
    return None
