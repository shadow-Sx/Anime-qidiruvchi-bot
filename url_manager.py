# url_manager.py
import json
import os

URLS_FILE = "anime_urls.json"

def load_urls():
    """JSON fayldan URL lug'atini yuklash."""
    if not os.path.exists(URLS_FILE):
        return {}
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_urls(data):
    """URL lug'atini JSON faylga saqlash."""
    with open(URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_url(anime_name):
    """Berilgan anime nomi uchun URL qaytarish."""
    urls = load_urls()
    return urls.get(anime_name)

def set_url(anime_name, url):
    """Yangi URL qo'shish yoki mavjudini yangilash."""
    urls = load_urls()
    urls[anime_name] = url
    save_urls(urls)

def delete_url(anime_name):
    """URL ni o'chirish."""
    urls = load_urls()
    if anime_name in urls:
        del urls[anime_name]
        save_urls(urls)
        return True
    return False
