import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings():
    # Database
    MONGO_URI: str = os.getenv("MONGO_URI")
    NEO4J_URI: str = os.getenv("NEO4J_URI")
    NEO4J_USER: str = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD")

    # Clerk Authentication
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY")

    # Messaging Queue
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(', ')

# Initialize settings
settings = Settings()
