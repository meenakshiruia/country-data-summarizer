import string  # Add this import at the top of the file

# Define the population density prompt with placeholders for data
POPULATION_DENSITY_PROMPT = """
Analyze the population density and urbanization trends of {country_name}. Consider the following aspects:
1. Total population: {population}
2. Urban population: {urban_population} ({urban_population_percentage:.2f}% of total)
3. Urban population growth rate: {urban_population_growth:.2f}%
4. Population density: {population_density:.2f} people per square kilometer
5. Comparison to global average population density
6. Implications of urbanization rate on infrastructure and resources
7. Potential challenges or opportunities presented by the current population distribution

Provide a concise summary of these aspects, highlighting any notable characteristics or trends related to {country_name}'s population density and urbanization.
"""

# Define the trade prompt
TRADE_PROMPT = """
Examine the trade profile and economic indicators of {country_name}. Focus on:
1. Gross Domestic Product (GDP): ${gdp} billion
2. GDP growth rate: {gdp_growth:.2f}%
3. GDP per capita: ${gdp_per_capita}
4. Trade to GDP ratio: {trade_to_gdp_ratio:.2f}%
5. Comparison of GDP growth to global and regional averages
6. Analysis of GDP per capita in relation to country's development status
7. Implications of current GDP growth rate on future economic prospects
8. Factors contributing to or hindering economic growth

Summarize the key points about {country_name}'s economic situation, including strengths, weaknesses, and potential future developments based on these trade and GDP indicators.
"""

# Define the import/export prompt
IMPORT_EXPORT_PROMPT = """
Analyze the import and export patterns of {country_name}. Consider:
1. Total exports: ${exports} billion
2. Total imports: ${imports} billion
3. Trade balance: ${trade_balance} billion ({trade_balance_status})
4. Export to GDP ratio: {exports_to_gdp_ratio:.2f}%
5. Import to GDP ratio: {imports_to_gdp_ratio:.2f}%
6. Major export sectors or products (if data available)
7. Major import sectors or products (if data available)
8. Trade openness index: {trade_openness_index:.2f}%

Provide a summary of {country_name}'s import and export characteristics, highlighting any trade surpluses or deficits, the country's level of trade openness, and potential areas for trade diversification or improvement.
"""

# Define the comprehensive prompt
COMPREHENSIVE_PROMPT = """
Provide a comprehensive economic summary for {country_name} based on the following data:

1. Population and Urbanization:
   - Total population: {population}
   - Urban population: {urban_population} ({urban_population_percentage:.2f}% of total)
   - Urban population growth rate: {urban_population_growth:.2f}%
   - Population density: {population_density:.2f} people per square kilometer

2. Economic Indicators:
   - Gross Domestic Product (GDP): ${gdp} billion
   - GDP growth rate: {gdp_growth:.2f}%
   - GDP per capita: ${gdp_per_capita}

3. Trade Profile:
   - Exports: ${exports} billion
   - Imports: ${imports} billion
   - Trade balance: ${trade_balance} billion ({trade_balance_status})
   - Trade to GDP ratio: {trade_to_gdp_ratio:.2f}%
   - Export to GDP ratio: {exports_to_gdp_ratio:.2f}%
   - Import to GDP ratio: {imports_to_gdp_ratio:.2f}%
   - Trade openness index: {trade_openness_index:.2f}%

Analyze these aspects and provide a concise summary of {country_name}'s economic situation, including:
1. Overall economic health and growth prospects
2. Urbanization trends and their implications
3. Trade profile and international economic integration
4. Key strengths and challenges in the economy
5. Potential areas for economic development or policy focus

Limit your response to about 250-300 words.
"""
# Function to retrieve the appropriate prompt based on the parameter
def get_prompt_for_parameter(parameter):
    prompts = {
        "population_density": POPULATION_DENSITY_PROMPT,
        "trade": TRADE_PROMPT,
        "import_export": IMPORT_EXPORT_PROMPT,
    }
    return prompts.get(parameter.lower(), "No specific prompt available for this parameter.")

def get_comprehensive_prompt():
    return COMPREHENSIVE_PROMPT

def format_prompt(prompt, country_name, data):
    # Create a copy of the data to avoid modifying the original
    formatted_data = data.copy()

    # Add country_name to the data dictionary
    formatted_data['country_name'] = country_name

    # Helper function to safely get values and perform calculations
    def safe_calc(operation, default=0):
        try:
            return operation()
        except (KeyError, TypeError, ZeroDivisionError):
            return default

    # Calculate additional metrics
    formatted_data['urban_population_percentage'] = safe_calc(lambda: (formatted_data.get('urban_population', 0) / formatted_data.get('population', 1)) * 100)
    formatted_data['population_density'] = safe_calc(lambda: formatted_data.get('population', 0) / formatted_data.get('surface_area', 1))
    formatted_data['trade_to_gdp_ratio'] = safe_calc(lambda: ((formatted_data.get('exports', 0) + formatted_data.get('imports', 0)) / formatted_data.get('gdp', 1)) * 100)
    formatted_data['trade_balance'] = safe_calc(lambda: formatted_data.get('exports', 0) - formatted_data.get('imports', 0))
    formatted_data['trade_balance_status'] = 'surplus' if formatted_data['trade_balance'] > 0 else 'deficit'
    formatted_data['exports_to_gdp_ratio'] = safe_calc(lambda: (formatted_data.get('exports', 0) / formatted_data.get('gdp', 1)) * 100)
    formatted_data['imports_to_gdp_ratio'] = safe_calc(lambda: (formatted_data.get('imports', 0) / formatted_data.get('gdp', 1)) * 100)
    formatted_data['trade_openness_index'] = safe_calc(lambda: ((formatted_data.get('exports', 0) + formatted_data.get('imports', 0)) / formatted_data.get('gdp', 1)) * 100)

    # Ensure all required fields are present, use placeholders if missing
    required_fields = ['population', 'urban_population', 'urban_population_growth', 'gdp', 'gdp_growth', 'gdp_per_capita', 'exports', 'imports', 'surface_area']
    for field in required_fields:
        if field not in formatted_data or formatted_data[field] is None:
            formatted_data[field] = "N/A"

    # Format numbers for better readability
    for key, value in formatted_data.items():
        if isinstance(value, (int, float)):
            if abs(value) >= 1e9:
                formatted_data[key] = f"{value/1e9:.2f} billion"
            elif abs(value) >= 1e6:
                formatted_data[key] = f"{value/1e6:.2f} million"
            elif abs(value) >= 1e3:
                formatted_data[key] = f"{value/1e3:.2f} thousand"
            else:
                formatted_data[key] = f"{value:.2f}"
        elif value == "N/A":
            formatted_data[key] = "N/A"

    # Use a custom formatter to handle the formatting
    class CustomFormatter(string.Formatter):
        def format_field(self, value, format_spec):
            if format_spec.endswith('f') and not isinstance(value, (int, float)):
                return value  # Return the value as-is if it's not a number
            return super().format_field(value, format_spec)

    formatter = CustomFormatter()
    return formatter.format(prompt, **formatted_data)
