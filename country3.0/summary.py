import logging
from groq import Groq
import os

# Set up logging
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
groq_client = Groq(api_key=GROQ_API_KEY)

def get_country_data_summary(country_data):
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
        return {"country": country_data['country_name'], "summary": summary}
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return None
