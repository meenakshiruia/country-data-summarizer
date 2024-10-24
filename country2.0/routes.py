from flask import jsonify, request
from services import (
    fetch_country_data, store_country_data, get_country_data, get_country_data_summary,
    fetch_economy_data, store_economy_data, get_economy_data
)
from prompts import get_prompt_for_parameter, format_prompt, get_comprehensive_prompt
from groq import Groq
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_summary(prompt):
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates concise summaries based on economic data."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="mixtral-8x7b-32768",
            max_tokens=500,
            temperature=0.7,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return None

def setup_routes(app):
    @app.route('/country/<country_name>')
    def get_country_data_route(country_name):
        country_data = get_country_data(country_name)
        if country_data:
            return jsonify(country_data)
        else:
            # If not in database, try to fetch from API
            fetched_data = fetch_country_data(country_name)
            if fetched_data:
                store_country_data(fetched_data)
                return jsonify(fetched_data)
            else:
                return jsonify({"error": "Country not found"}), 404
    @app.route('/fetch-and-store/<country_name>')
    def fetch_and_store_country(country_name):
        country_data = fetch_country_data(country_name)
        if country_data:
            store_country_data(country_data)
            return jsonify({"message": f"Data for {country_name} fetched and stored successfully"})
        else:
            return jsonify({"error": "Failed to fetch country data"}), 404

    @app.route('/country-summary/<country_name>')
    def get_country_summary(country_name):
        summary = get_country_data_summary(country_name)
        if summary:
            return jsonify(summary)
        else:
            return jsonify({"error": "Country not found"}), 404
        
    @app.route('/fetch-and-store-economy/<country_name>', methods=['GET', 'POST'])
    def fetch_and_store_economy(country_name):
        economy_data = fetch_economy_data(country_name)
        if economy_data:
            store_economy_data(country_name, economy_data)
            return jsonify({"message": f"Economy data for {country_name} fetched and stored successfully", "data": economy_data})
        else:
            error_message = f"Failed to fetch economy data for {country_name}. Please check server logs for more details."
            logger.error(error_message)
            return jsonify({"error": error_message}), 404

    @app.route('/economy/<country_name>')
    def get_economy_data_route(country_name):
        economy_data = get_economy_data(country_name)
        if economy_data:
            return jsonify(economy_data)
        else:
            return jsonify({"error": "Economy data not found"}), 404

    @app.route('/country-parameter-summary/<country_name>')
    def get_country_parameter_summary(country_name):
        parameter = request.args.get('parameter', '').lower()
        valid_parameters = ['population_density', 'trade', 'import_export']
        
        country_data = get_country_data(country_name)
        economy_data = get_economy_data(country_name)
        
        if not country_data and not economy_data:
            country_data = fetch_country_data(country_name)
            economy_data = fetch_economy_data(country_name)
            if country_data:
                store_country_data(country_data)
            if economy_data:
                store_economy_data(country_name, economy_data)
        
        if not country_data and not economy_data:
            return jsonify({"error": "Country data not found"}), 404
        
        # Combine country_data and economy_data
        combined_data = {**country_data, **economy_data} if country_data and economy_data else country_data or economy_data or {}
        
        try:
            if parameter in valid_parameters:
                prompt = get_prompt_for_parameter(parameter)
            else:
                prompt = get_comprehensive_prompt()
            
            formatted_prompt = format_prompt(prompt, country_name, combined_data)
            summary = generate_summary(formatted_prompt)
            
            if summary:
                return jsonify({"summary": summary})
            else:
                return jsonify({"error": "Failed to generate summary"}), 500
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return jsonify({"error": f"Error processing request: {str(e)}"}), 500
