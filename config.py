# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot tokeni
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Admin Telegram ID (faqat siz boshqarishingiz uchun)
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
    
    # Render.com dagi ilova manzili
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://your-app.onrender.com")
    
    # Port (Render avtomatik beradi)
    PORT = int(os.getenv("PORT", "8080"))
    
    # Jikan API sozlamalari
    JIKAN_BASE_URL = "https://api.jikan.moe/v4"
    
    # Google Translate API (agar keyinroq qo'shsangiz)
    GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", None)
    
    # Kesh sozlamalari (ixtiyoriy)
    CACHE_TTL = 300  # 5 daqiqa

config = Config()
