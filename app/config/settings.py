import os

from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    print("Warning: .env file not found. Relying on environment variables.")

load_dotenv()
try:
    DB_URI = os.environ["DB_URI"]
    SECRET_KEY = os.environ["SECRET_KEY"]
except KeyError as e:
    raise RuntimeError(f"Missing required environment variable: {e.args[0]}")

SQLA_TRACK_MODIFICATIONS = False

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t", "yes")

CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "").strip().split(",")
