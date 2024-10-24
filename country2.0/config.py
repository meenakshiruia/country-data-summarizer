import os
import psycopg2
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=int(os.getenv('DB_PORT', 5432))
        )
        return connection
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def setup_database():
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to the database. Cannot set up tables.")
        return

    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS country_economy (
            country_name VARCHAR(255) PRIMARY KEY,
            surface_area FLOAT,
            exports FLOAT,
            tourists FLOAT,
            gdp FLOAT,
            population BIGINT,
            imports FLOAT,
            urban_population_growth FLOAT,
            urban_population BIGINT,
            gdp_growth FLOAT,
            gdp_per_capita FLOAT
        );
        """)
        
        conn.commit()
        logger.info("Database setup completed successfully.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error setting up database: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database()