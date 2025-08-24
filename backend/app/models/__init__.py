from mongoengine import connect, disconnect

def initialize_db(app):
    """Initialize MongoEngine connection using MongoDB URI."""
    uri = app.config.get("MONGODB_URI")

    if not uri:
        raise ValueError("⚠️ MONGODB_URI is not set in app config")

    try:
        # Ensure any old connection is closed
        disconnect(alias="default")
        
        # Connect using MongoDB URI
        connect(host=uri, alias="default")
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise e