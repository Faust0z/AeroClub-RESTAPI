import os

from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    raise FileNotFoundError(".env file not found. Please create one before running the app.")

load_dotenv()
DB_URI = os.getenv("DB_URI")
SQLA_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG")

# CORS allowed origins (comma-separated in .env)
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS").split(",")
