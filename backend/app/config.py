import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
    CACHE_TTL = 3600
