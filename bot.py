#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import asyncio
from html import escape
from typing import List, Optional

# Telegram kutubxonalari
from telegram import (
    Update, InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    InlineQueryHandler
)

# Tashqi API'lar
import requests
from dotenv import load_dotenv

# Starlette webhook uchun
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.requests import Request
from starlette.routing import Route
import uvicorn

# ----------------------------------------------------------------------
# SOZLAMALAR
# ----------------------------------------------------------------------
load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://your-app.onrender.com")
PORT = int(os.environ.get("PORT", 8080))

# Jikan API sozlamalari
JIKAN_BASE = "https://api.jikan.moe/v4"

# Logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin kanal uchun URL'lar (Keyinroq admin panel qo'shasiz)
ANIME_WATCH_URLS = {
    "Jujutsu Kaisen": "https://t.me/yourchannel/jjk",
    "Naruto": "https://t.me/yourchannel/naruto",
    "Bleach": "https://t.me/yourchannel/bleach",
}

# ----------------------------------------------------------------------
# JIKAN API FUNKSIYALARI
# ----------------------------------------------------------------------

def search_anime(query: str, limit: int = 5) -> List[dict]:
    try:
        resp = requests.get(
            f"{JIKAN_BASE}/anime",
            params={"q": query, "limit": limit},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json().get("data", [])
    except Exception as e:
        logger.error(f"Anime qidirish xatosi: {e}")
    return []

def search_characters(query: str, limit: int = 5) -> List[dict]:
    try:
        resp = requests.get(
            f"{JIKAN_BASE}/characters",
            params={"q": query, "limit": limit},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json().get("data", [])
    except Exception as e:
        logger.error(f"Personaj qidirish xatosi: {e}")
    return []

# ----------------------------------------------------------------------
# BOT HANDLERLARI
# ----------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🔍 Qidirish", switch_inline_query_current_chat="")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "🎌 *Anime Qidiruv Bot* ga xush kelibsiz!\n\n"
        "Men sizga anime va personajlar haqida ingliz tilida ma'lumot beraman.\n\n"
        "👇 Quyidagi tugmani bosing yoki istalgan chatda `@botusername` deb yozing:"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query.strip()
    if not query:
        await update.inline_query.answer([])
        return

    results = []

    # --- Personajlar ---
    characters = search_characters(query)
    for char in characters:
        char_id = char.get("mal_id")
        name = char.get("name", "Noma'lum")
        about = char.get("about", "")
        desc = about[:300] + "..." if len(about) > 300 else about

        anime_names = []
        if char.get("anime"):
            for a in char["anime"][:3]:
                anime_names.append(a.get("anime", {}).get("title", ""))
        anime_list = ", ".join(anime_names) if anime_names else "Noma'lum"

        thumb_url = char.get("images", {}).get("jpg", {}).get("image_url")

        result_text = (
            f"👤 *{escape(name)}*\n\n"
            f"📺 *Anime:* {escape(anime_list)}\n\n"
            f"📝 *About:* {escape(desc)}"
        )

        keyboard = []
        if anime_names:
            first_anime = anime_names[0]
            watch_url = ANIME_WATCH_URLS.get(first_anime, "https://t.me/yourchannel")
            keyboard.append([InlineKeyboardButton("🎬 Animeni ko'rish", url=watch_url)])
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        results.append(
            InlineQueryResultArticle(
                id=f"char_{char_id}",
                title=f"👤 {name}",
                description=f"📺 {anime_list}",
                thumbnail_url=thumb_url,
                input_message_content=InputTextMessageContent(result_text, parse_mode=ParseMode.MARKDOWN),
                reply_markup=reply_markup
            )
        )

    # --- Animelar ---
    animes = search_anime(query)
    for anime in animes:
        anime_id = anime.get("mal_id")
        title = anime.get("title", "Noma'lum")
        title_eng = anime.get("title_english") or title
        synopsis = anime.get("synopsis", "")
        desc = synopsis[:300] + "..." if len(synopsis) > 300 else synopsis

        thumb_url = anime.get("images", {}).get("jpg", {}).get("image_url")
        episodes = anime.get("episodes", "Noma'lum")
        score = anime.get("score", "Noma'lum")
        year = anime.get("year") or "Noma'lum"

        result_text = (
            f"🎬 *{escape(title)}*\n"
            f"🇬🇧 *{escape(title_eng)}*\n\n"
            f"📅 *Year:* {year}\n"
            f"📊 *Episodes:* {episodes}\n"
            f"⭐ *Score:* {score}\n\n"
            f"📝 *Synopsis:* {escape(desc)}"
        )

        watch_url = ANIME_WATCH_URLS.get(title, "https://t.me/yourchannel")
        keyboard = [[InlineKeyboardButton("🎬 Animeni ko'rish", url=watch_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        results.append(
            InlineQueryResultArticle(
                id=f"anime_{anime_id}",
                title=f"🎬 {title}",
                description=f"📅 {year} | ⭐ {score}",
                thumbnail_url=thumb_url,
                input_message_content=InputTextMessageContent(result_text, parse_mode=ParseMode.MARKDOWN),
                reply_markup=reply_markup
            )
        )

    await update.inline_query.answer(results, cache_time=0)

# ----------------------------------------------------------------------
# WEBHOOK VA SERVER
# ----------------------------------------------------------------------

async def webhook(request: Request) -> Response:
    try:
        body = await request.json()
        async with application:
            await application.process_update(Update.de_json(body, application.bot))
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status_code=500)

async def healthcheck(request: Request) -> Response:
    return Response("OK", status_code=200)

# ----------------------------------------------------------------------
# ASOSIY DASTUR
# ----------------------------------------------------------------------

if __name__ == "__main__":
    application = Application.builder().token(BOT_TOKEN).updater(None).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inline_query))

    webhook_url = f"{RENDER_URL}/webhook"

    starlette_app = Starlette(
        routes=[
            Route("/webhook", webhook, methods=["POST"]),
            Route("/healthcheck", healthcheck, methods=["GET"]),
        ]
    )

    async def main():
        await application.initialize()
        await application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
        config = uvicorn.Config(starlette_app, host="0.0.0.0", port=PORT, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")
    finally:
        asyncio.run(application.shutdown())
