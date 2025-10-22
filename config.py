"""
config.py - Konfigurasi Aplikasi
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Basis Data
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # AI
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "qwen/qwen3-32b"
    
    # Aplikasi
    APP_TITLE = "Talent Match Intelligence"
    PAGE_ICON = "🎯"
    DEFAULT_TOP_N = 10
    CACHE_TTL = 3600  # 1 jam
    
    # Ambang Batas
    EXCELLENT_MATCH = 90.0
    GOOD_MATCH = 70.0
    MIN_BENCHMARKS = 1
    RECOMMENDED_BENCHMARKS = 3

# Validasi kunci yang diperlukan
def validate_config():
    if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL dan SUPABASE_KEY harus diset di .env")
    if not Config.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY harus diset di .env")

validate_config()