import os
from dotenv import load_dotenv

load_dotenv()

SECRET_API_KEY = os.getenv('SECRET_API_KEY', 'a-secret-api-key-placeholder')
