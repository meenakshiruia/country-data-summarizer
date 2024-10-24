from flask import Flask
from dotenv import load_dotenv
from routes import setup_routes
from config import setup_database

# Load environment variables
load_dotenv()

# Flask application setup
app = Flask(__name__)

# Setup database
setup_database()

# Setup routes
setup_routes(app)

if __name__ == '__main__':
    app.run(debug=True)