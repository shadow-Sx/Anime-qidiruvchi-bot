# url_manager.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["anime_bot_db"]
urls_collection = db["urls"]

def load_urls():
    """URL'larni lug'at ko'rinishida qaytarish."""
    urls = {}
    for doc in urls_collection.find():
        urls[doc["anime_name"]] = doc["url"]
    return urls

def get_url(anime_name):
    """Berilgan anime nomi uchun URL qaytarish."""
    doc = urls_collection.find_one({"anime_name": anime_name})
    return doc["url"] if doc else None

def set_url(anime_name, url):
    """Yangi URL qo'shish yoki mavjudini yangilash."""
    urls_collection.update_one(
        {"anime_name": anime_name},
        {"$set": {"url": url}},
        upsert=True
    )

def delete_url(anime_name):
    """URL ni o'chirish."""
    result = urls_collection.delete_one({"anime_name": anime_name})
    return result.deleted_count > 0
