import os
import requests
from config import get_db_connection
from groq import Groq
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your API keys
API_KEY = os.getenv('YOUR_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
groq_client = Groq(api_key=GROQ_API_KEY)

def fetch_country_data(country_name):
    """Fetches country data from an external API."""
    api_url = f"https://api.api-ninjas.com/v1/country?name={country_name}"
    response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
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
    return None

def store_country_data(data):
    """Stores country data in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    insert_query = """
    INSERT INTO country_economy (
        country_name, surface_area, exports, tourists, gdp, population,
        imports, urban_population_growth, urban_population, gdp_growth, gdp_per_capita
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (country_name) DO UPDATE SET
        surface_area = EXCLUDED.surface_area,
        exports = EXCLUDED.exports,
        tourists = EXCLUDED.tourists,
        gdp = EXCLUDED.gdp,
        population = EXCLUDED.population,
        imports = EXCLUDED.imports,
        urban_population_growth = EXCLUDED.urban_population_growth,
        urban_population = EXCLUDED.urban_population,
        gdp_growth = EXCLUDED.gdp_growth,
        gdp_per_capita = EXCLUDED.gdp_per_capita;
    """
    
    cursor.execute(insert_query, (
        data['country_name'],
        float(data.get('surface_area', 0)),
        float(data.get('exports', 0)),
        float(data.get('tourists', 0)),
        float(data.get('gdp', 0)),
        int(data.get('population', 0)),
        float(data.get('imports', 0)),
        float(data.get('urban_population_growth', 0)),
        int(data.get('urban_population', 0)),
        float(data.get('gdp_growth', 0)),
        float(data.get('gdp_per_capita', 0))
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

def get_country_data(country_name):
    """Retrieves country data from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM country_economy WHERE country_name = %s", (country_name,))
    country_data = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if country_data:
        return {
            "country_name": country_data[0],
            "surface_area": country_data[1],
            "exports": country_data[2],
            "tourists": country_data[3],
            "gdp": country_data[4],
            "population": country_data[5],
            "imports": country_data[6],
            "urban_population_growth": country_data[7],
            "urban_population": country_data[8],
            "gdp_growth": country_data[9],
            "gdp_per_capita": country_data[10]
        }
    return None
def get_country_data_summary(country_name):
    """Generates a summary for the specified country."""
    country_data = get_country_data(country_name)
    if not country_data:
        return None

    prompt = f"""Generate a concise summary for {country_data['country_name']} based on the following data:
    Surface Area: {country_data['surface_area']} sq km
    Exports: ${country_data['exports']} billion
    Annual Tourists: {country_data['tourists']} million
    GDP: ${country_data['gdp']} billion
    Population: {country_data['population']}

    Provide insights on the country's economy, tourism, and demographics in a paragraph."""

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates concise country summaries based on provided data."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="mixtral-8x7b-32768", 
            max_tokens=200
        )

        summary = response.choices[0].message.content.strip()
        return {"country": country_name, "summary": summary}
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return None
    
def store_economy_data(country_name, data):
    """Stores country economic data in the country_economy table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO country_economy (
        country_name, imports, urban_population_growth, exports,
        population, urban_population, gdp, gdp_growth, gdp_per_capita
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (country_name) DO UPDATE SET
        imports = EXCLUDED.imports,
        urban_population_growth = EXCLUDED.urban_population_growth,
        exports = EXCLUDED.exports,
        population = EXCLUDED.population,
        urban_population = EXCLUDED.urban_population,
        gdp = EXCLUDED.gdp,
        gdp_growth = EXCLUDED.gdp_growth,
        gdp_per_capita = EXCLUDED.gdp_per_capita;
    """

    try:
        cursor.execute(insert_query, (
            country_name,
            data.get('imports', 0),
            data.get('urban_population_growth', 0),
            data.get('exports', 0),
            data.get('population', 0),
            data.get('urban_population', 0),
            data.get('gdp', 0),
            data.get('gdp_growth', 0),
            data.get('gdp_per_capita', 0)
        ))
        conn.commit()
        logger.info(f"Economy data for {country_name} stored successfully.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error storing economy data for {country_name}: {str(e)}")
    finally:
        cursor.close()
        conn.close()
def get_economy_data(country_name):
    """Retrieves economy data from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM country_economy WHERE country_name = %s", (country_name,))
    economy_data = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if economy_data:
        return {
            "country_name": economy_data[0],  # Assuming country_name is the first column
            "imports": economy_data[1],
            "urban_population_growth": economy_data[2],
            "exports": economy_data[3],
            "population": economy_data[4],
            "urban_population": economy_data[5],
            "gdp": economy_data[6],
            "gdp_growth": economy_data[7],
            "gdp_per_capita": economy_data[8],
            "surface_area": economy_data[9] if len(economy_data) > 9 else 0
        }
    return None

def fetch_economy_data(country_name):
    """Fetches country data including economic indicators."""
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
