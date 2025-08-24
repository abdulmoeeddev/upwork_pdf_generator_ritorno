import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment variables
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print(f"🚀 Starting Upwork Proposal Generator API...")
    print(f"📍 Running on http://{host}:{port}")
    print(f"🐛 Debug mode: {debug}")
    
    app.run(
        debug=debug, 
        host=host, 
        port=port,
        threaded=True
    )