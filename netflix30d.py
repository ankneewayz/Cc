#!/usr/bin/env python3
"""
Netflix 30-Day Trial Telegram Bot
Owner: @ankneewayz
Direct Pinterest video fetching — no catbox, no file_id tricks
"""

import asyncio
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from telegram.constants import ParseMode
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Tuple

import requests
import yt_dlp
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ═══════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════

BOT_TOKEN = os.getenv("BOT_TOKEN", "8760415886:AAH-JhrbqKGtfyc_-zJ4ewGedle2Q-vvJj0")

REQUIRED_CHANNEL = "@J4KERS"
REQUIRED_GROUP   = "@ankneewayzgrp"
OWNER_ID = int(os.getenv("OWNER_ID", "8598993143"))

COOKIE_SERVER_URL = os.getenv("COOKIE_SERVER_URL", "http://85.115.209.225:3739")
COOKIE_API_KEY    = os.getenv("COOKIE_API_KEY", "NetflixCookie2026!@#")

FREE_USER_DAILY_LIMIT   = 1
PREMIUM_USER_DAILY_LIMIT = 999999

# ═══════════════════════════════════════════════════════════════════
#  PINTEREST START VIDEO  —  change this to your pin URL
# ═══════════════════════════════════════════════════════════════════

PINTEREST_PIN_URL = os.getenv(
    "PINTEREST_PIN_URL",
    "https://pin.it/74dHtPHGO"  # ← PUT YOUR PIN URL HERE
)

def fetch_pinterest_video() -> Optional[str]:
    """
    Extract a direct playable MP4 URL from a Pinterest pin using yt-dlp.
    Returns None if it fails.
    """
    try:
        ydl_opts = {
    "format": "best",
    "quiet": True,
    "no_warnings": True,
}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(PINTEREST_PIN_URL, download=False)
            # YouTubeDL returns the direct video URL in 'url' for single-format requests
            if 'url' in info:
                return info['url']
            # Fallback: iterate formats
            if 'formats' in info and info['formats']:
                # Prefer mp4, highest quality
                for f in info['formats']:
                    if f.get('ext') == 'mp4' and f.get('url'):
                        return f['url']
                # Any format with a url
                for f in info['formats']:
                    if f.get('url'):
                        return f['url']
        return None
    except Exception as e:
        print(f"  [!] Pinterest fetch failed: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════
#  DB
# ═══════════════════════════════════════════════════════════════════

DB_PATH = "netflix_bot.db"

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id    INTEGER PRIMARY KEY,
            username   TEXT,
            role       TEXT NOT NULL DEFAULT 'free',
            is_active  INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS email_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL,
            email     TEXT NOT NULL,
            success   INTEGER NOT NULL,
            detail    TEXT,
            sent_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS cookies (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cookie_text TEXT NOT NULL,
            cookie_type TEXT,
            is_active   INTEGER NOT NULL DEFAULT 1,
            added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    if OWNER_ID:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, role) VALUES (?, ?, 'premium')",
            (OWNER_ID, "owner"),
        )
        conn.execute("UPDATE users SET role='premium' WHERE user_id=?", (OWNER_ID,))
    conn.commit()
    conn.close()

def get_user(user_id: int) -> Optional[sqlite3.Row]:
    conn = get_db()
    cur = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row

def create_user(user_id: int, username: str = None):
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username),
    )
    conn.commit()
    conn.close()

def set_user_role(user_id: int, role: str):
    conn = get_db()
    conn.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, user_id))
    conn.commit()
    conn.close()

def get_user_role(user_id: int) -> str:
    u = get_user(user_id)
    return u["role"] if u else "free"

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

def is_premium(user_id: int) -> bool:
    role = get_user_role(user_id)
    return role == "premium" or is_owner(user_id)

def get_today_count(user_id: int) -> int:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    conn = get_db()
    cur = conn.execute(
        "SELECT COUNT(*) as cnt FROM email_log WHERE user_id = ? AND DATE(sent_at) = ?",
        (user_id, today),
    )
    row = cur.fetchone()
    conn.close()
    return row["cnt"] if row else 0

def can_claim_today(user_id: int) -> Tuple[bool, str]:
    if is_owner(user_id):
        return True, "unlimited"
    if is_premium(user_id):
        return True, "premium"
    cnt = get_today_count(user_id)
    if cnt >= FREE_USER_DAILY_LIMIT:
        return False, f"daily limit ({FREE_USER_DAILY_LIMIT}/day) reached"
    return True, "free"

def log_email(user_id: int, email: str, success: bool, detail: str = ""):
    conn = get_db()
    conn.execute(
        "INSERT INTO email_log (user_id, email, success, detail) VALUES (?, ?, ?, ?)",
        (user_id, email, 1 if success else 0, detail),
    )
    conn.commit()
    conn.close()

def save_cookie(cookie_text: str, cookie_type: str = "json"):
    conn = get_db()
    conn.execute(
        "INSERT INTO cookies (cookie_text, cookie_type) VALUES (?, ?)",
        (cookie_text, cookie_type),
    )
    conn.commit()
    conn.close()

def get_active_cookies() -> list:
    conn = get_db()
    cur = conn.execute(
        "SELECT * FROM cookies WHERE is_active = 1 ORDER BY added_at DESC LIMIT 50"
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def deactivate_cookie(cookie_id: int):
    conn = get_db()
    conn.execute("UPDATE cookies SET is_active = 0 WHERE id = ?", (cookie_id,))
    conn.commit()
    conn.close()

# ═══════════════════════════════════════════════════════════════════
#  NETFLIX SERVICE
# ═══════════════════════════════════════════════════════════════════

def parse_netscape_cookie(cookie_text: str) -> dict:
    cookies = {}
    for line in cookie_text.strip().split('\n'):
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        parts = line.split('\t')
        if len(parts) >= 7:
            cookies[parts[5]] = parts[6]
    return cookies

def parse_json_cookie(json_text: str) -> dict:
    try:
        data = json.loads(json_text)
        cookies = {}
        if isinstance(data, dict):
            for k, v in data.items():
                cookies[k] = str(v)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    if 'name' in item and 'value' in item:
                        cookies[item['name']] = item['value']
                    elif 'key' in item and 'value' in item:
                        cookies[item['key']] = item['value']
        return cookies
    except Exception:
        return {}

def parse_cookie_content(content: str) -> Tuple[Optional[dict], Optional[str]]:
    content = content.strip()
    if content.startswith('{') or content.startswith('['):
        cookies = parse_json_cookie(content)
        if cookies and ('NetflixId' in cookies or 'SecureNetflixId' in cookies):
            return cookies, "JSON"
    cookies = parse_netscape_cookie(content)
    if cookies and ('NetflixId' in cookies or 'SecureNetflixId' in cookies):
        return cookies, "Netscape"
    cookies = {}
    for line in content.split('\n'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            parts = line.split('=', 1)
            if len(parts) == 2:
                cookies[parts[0].strip()] = parts[1].strip()
    if cookies and ('NetflixId' in cookies or 'SecureNetflixId' in cookies):
        return cookies, "Simple"
    return None, None

def build_cookie_string(cookies: dict) -> str:
    return "; ".join(f"{k}={v}" for k, v in cookies.items())

def extract_flwssn(cookie_string: str) -> str:
    m = re.search(r'flwssn=([^;]+)', cookie_string)
    return m.group(1) if m else str(uuid.uuid4())

def extract_gsid(cookie_string: str) -> str:
    m = re.search(r'gsid=([^;]+)', cookie_string)
    return m.group(1) if m else str(uuid.uuid4())

def generate_request_id() -> str:
    return uuid.uuid4().hex[:32]

def generate_toplevel_uuid() -> str:
    return str(uuid.uuid4())

def fetch_cookies_from_server() -> Tuple[Optional[dict], Optional[str]]:
    try:
        headers = {"X-API-Key": COOKIE_API_KEY}
        resp = requests.get(f"{COOKIE_SERVER_URL}/get-cookie", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if 'cookies' in data:
                return parse_cookie_content(data['cookies'])
        return None, None
    except Exception:
        return None, None

def send_trial_offer(email: str, cookie_string: str) -> Tuple[dict, bool]:
    flwssn = extract_flwssn(cookie_string)
    gsid = extract_gsid(cookie_string)

    base_headers = {
        'authority': 'web.prod.cloud.netflix.com',
        'accept': '*/*',
        'accept-language': 'en-MM,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://www.netflix.com',
        'referer': 'https://www.netflix.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }

    results = {}

    # Step 1: CLCSWebInitSignup
    try:
        h = base_headers.copy()
        h.update({
            'content-type': 'application/json',
            'cookie': cookie_string,
            'x-netflix.context.app-version': 'v38c5b0da',
            'x-netflix.context.form-factor': 'phone',
            'x-netflix.context.is-inapp-browser': 'false',
            'x-netflix.context.locales': 'en-in',
            'x-netflix.context.operation-name': 'CLCSWebInitSignup',
            'x-netflix.context.ui-flavor': 'akira',
            'x-netflix.request.attempt': '1',
            'x-netflix.request.clcs.bucket': 'high',
            'x-netflix.request.client.context': '{"appstate":"foreground"}',
            'x-netflix.request.id': generate_request_id(),
            'x-netflix.request.originating.url': 'https://www.netflix.com/in/',
            'x-netflix.request.toplevel.uuid': generate_toplevel_uuid(),
        })
        payload = {
            "operationName": "CLCSWebInitSignup",
            "variables": {
                "inputNode": "WELCOME",
                "locale": "en-IN",
                "inputFields": [
                    {"name": "flwssn", "value": {"stringValue": flwssn}},
                    {"name": "email", "value": {"stringValue": email}},
                    {"name": "recaptchaError", "value": {"stringValue": "LOAD_TIMED_OUT"}},
                    {"name": "recaptchaResponseTime", "value": {}},
                    {"name": "recaptchaSiteKey", "value": {"stringValue": "6LdqW_EqAAAAAO87Fb_kcZfNzs0IqJRcKiJDYpUv"}},
                    {"name": "recaptchaToken", "value": {}},
                ],
            },
            "extensions": {
                "persistedQuery": {
                    "id": "5d76d6a0-ccfe-4c31-b587-b4e1954732ca",
                    "version": 102,
                }
            },
        }
        resp = requests.post(
            'https://web.prod.cloud.netflix.com/graphql',
            headers=h, json=payload, timeout=15,
        )
        results['init'] = {'status': resp.status_code}
        if resp.status_code != 200:
            return results, False
    except Exception as e:
        results['init'] = {'error': str(e)}
        return results, False

    # Step 2: CLCSScreenUpdate
    try:
        h2 = base_headers.copy()
        h2.update({
            'content-type': 'application/json',
            'cookie': cookie_string,
            'x-netflix.context.app-version': 'v38c5b0da',
            'x-netflix.context.form-factor': 'phone',
            'x-netflix.context.is-inapp-browser': 'false',
            'x-netflix.context.locales': 'en-in',
            'x-netflix.context.operation-name': 'CLCSScreenUpdate',
            'x-netflix.context.ui-flavor': 'akira',
            'x-netflix.request.attempt': '1',
            'x-netflix.request.clcs.bucket': 'high',
            'x-netflix.request.client.context': '{"appstate":"foreground"}',
            'x-netflix.request.id': generate_request_id(),
            'x-netflix.request.originating.url': 'https://www.netflix.com/signup',
            'x-netflix.request.toplevel.uuid': generate_toplevel_uuid(),
        })
        payload2 = {
            "operationName": "CLCSScreenUpdate",
            "variables": {
                "format": "HTML",
                "imageFormat": "PNG",
                "locale": "en-IN",
                "serverState": "Bgjru+vcAxLTAf/qOOEwXPLVxW+7Jod9WpjYuKN8j1qfhQpzCK4mmQts5eMSeaP+l7s6NKcNBO4rmYabFFCVnMpCH3ib4AicvXAKm30Z+s5W3Cst0D0BK5x/pwn3QmByi/OgGwU/fzaiR5oxSlZe4fKVexWHISkE4GMzJqLaaXQR0M73ynZB9idNBfqsz3RA5WJN+DGAbVUOZlWl8eZqffvQpp/5MGubeQFpdwKqkAx1nHh7/xI1i9tDU0KLgrvkZrbe6nQ1MX2nc9TBxqnVVxtc3ptHdqydP1wlIu0YBiIOCgydgLg1SvK6tSPOff8=",
                "serverScreenUpdate": "Bgjru+vcAxKSAjDnHOxlaIbFSbwaWzZo/REHFnNG7OtpcXdKTDlcL4/o+huGi/fNW+jrqNDqDSsv1iytiG/ZtvO9ierUE9M1Kc/yEj9JsSiG3XpPciFDzPd6psSaG68XLbos+Qie0wniXCtJyWDLDuLd9ayCMB8qGCxwbov6B41kCQY/zArwlecm0GNoJdd5jvZfBJVtytD6mMCYnPA/9zhX4okj+6IGet9xOCYt76IDiuyESxgKbaOLcd6DQIDSBf4m/lYi2Tasj7olPkCaDIXxjU+0UY+b7eDyhvi2if2vt6510ARrGsSZq8DaazQmrpAbfiCW47s1/1mR5vUMYeT8VCqqAvbNwipqyP1DQMHtoTnCoWns0+x6IgYBiIOCgx9EW4i3i9SUswnHEg=",
                "inputFields": [
                    {"name": "email", "value": {"stringValue": email}},
                    {"name": "pipcConsent", "value": {"booleanValue": False}},
                ],
            },
            "extensions": {
                "persistedQuery": {
                    "id": "0fd81de7-07af-4c7d-802f-0f4ea4181aa3",
                    "version": 102,
                }
            },
        }
        resp2 = requests.post(
            'https://web.prod.cloud.netflix.com/graphql',
            headers=h2, json=payload2, timeout=15,
        )
        results['update'] = {'status': resp2.status_code}
    except Exception as e:
        results['update'] = {'error': str(e)}

    # Step 3: Image fetch
    try:
        h3 = {
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-MM,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Referer': 'https://www.netflix.com/',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
        }
        img_url = 'https://occ-0-6711-64.1.nflxso.net/dnm/api/v6/QqNdfvCShgtu-ra1rla_KxCcSSY/AAAAQAmpros-eVHttd-jyVbIiMTW885cisEwMOLTGkTzHQifWIkevLiCu24tEsptsw.png?r=bff'
        resp3 = requests.get(img_url, headers=h3, timeout=10)
        results['image'] = {'status': resp3.status_code}
        if resp3.status_code == 200:
            return results, True
        return results, False
    except Exception as e:
        results['image'] = {'error': str(e)}
        return results, False

# ═══════════════════════════════════════════════════════════════════
#  MEMBERSHIP CHECK
# ═══════════════════════════════════════════════════════════════════

async def is_member(bot: Bot, user_id: int, chat_username: str) -> bool:
    if not chat_username:
        return True
    try:
        member = await bot.get_chat_member(chat_id=chat_username, user_id=user_id)
        return member.status in ("member", "administrator", "creator", "restricted")
    except Exception as e:
        print(f"  [!] is_member check failed for {chat_username}, user {user_id}: {e}")
        return False

def _build_membership_keyboard(in_channel: bool, in_group: bool):
    buttons = []
    if not in_channel and REQUIRED_CHANNEL:
        buttons.append(
            InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{REQUIRED_CHANNEL.lstrip('@')}")
        )
    if not in_group and REQUIRED_GROUP:
        buttons.append(
            InlineKeyboardButton("💬 Join Group", url=f"https://t.me/{REQUIRED_GROUP.lstrip('@')}")
        )
    if not buttons:
        return None
    buttons.append(InlineKeyboardButton("✅ I've Joined", callback_data="check_membership"))
    rows = []
    if len(buttons) == 3:
        rows.append(buttons[:2])
        rows.append([buttons[2]])
    elif len(buttons) == 2:
        rows.append([buttons[0]])
        rows.append([buttons[1]])
    else:
        rows = [[b] for b in buttons]
    return rows

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False
    if is_owner(user.id):
        return True
    bot = context.bot
    in_channel = await is_member(bot, user.id, REQUIRED_CHANNEL)
    in_group   = await is_member(bot, user.id, REQUIRED_GROUP)
    if in_channel and in_group:
        return True
    rows = _build_membership_keyboard(in_channel, in_group)
    reply_markup = InlineKeyboardMarkup(rows) if rows else None
    await update.effective_message.reply_text(
        "🚫 **Access Restricted**\n\n"
        "You must join our channel and group before using this bot:\n\n"
        f"• Channel: {REQUIRED_CHANNEL}\n"
        f"• Group:   {REQUIRED_GROUP}\n\n"
        "After joining, tap the button below to verify.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )
    return False

async def check_membership_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    bot = context.bot
    in_channel = await is_member(bot, user.id, REQUIRED_CHANNEL)
    in_group   = await is_member(bot, user.id, REQUIRED_GROUP)
    if in_channel and in_group:
        await query.edit_message_text(
            "✅ **You're all set!**\n\n"
            "You have joined both the channel and group.\n"
            "Now use `/claim` to send a trial offer!",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    missing = []
    if not in_channel:
        missing.append(f"📢 Channel: {REQUIRED_CHANNEL}")
    if not in_group:
        missing.append(f"💬 Group: {REQUIRED_GROUP}")
    await query.edit_message_text(
        "❌ **Still missing access to:**\n\n" +
        "\n".join(f"• {m}" for m in missing) +
        "\n\nPlease join and tap the button again.",
        parse_mode=ParseMode.MARKDOWN,
    )
    rows = _build_membership_keyboard(in_channel, in_group)
    if rows:
        await context.bot.send_message(
            chat_id=user.id,
            text="Tap below after joining:",
            reply_markup=InlineKeyboardMarkup(rows),
        )

# ═══════════════════════════════════════════════════════════════════
#  HANDLERS
# ═══════════════════════════════════════════════════════════════════

WAITING_EMAIL = range(1)

# ─── /start — fetches video directly from Pinterest ──────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user(user.id, user.username or user.first_name)

    role = get_user_role(user.id)
    role_label = "👑 **Owner**" if is_owner(user.id) else (
        "⭐ **Premium**" if is_premium(user.id) else "🆓 **Free**"
    )

    caption = (
        f"🎬 **Netflix Trial Bot**\n\n"
        f"Welcome, {user.first_name}!\n"
        f"Your role: {role_label}\n\n"
        "**Commands:**\n"
        "• `/claim` – Send a 30-day trial offer to any email\n"
        "• `/me` – Check your usage & role\n"
        "• `/help` – Show this help\n\n"
        f"Owner: @ankneewayz"
    )

    # Send a loading message first
    loading = await update.message.reply_text(
        "⏳ HOLD ON...",
        parse_mode=ParseMode.MARKDOWN,
    )

    # Fetch video URL from Pinterest
    video_url = fetch_pinterest_video()

    if video_url:
        try:
            await loading.delete()
            await update.message.reply_video(
                video=video_url,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                supports_streaming=True,
            )
            print(f"  [+] Sent Pinterest video to user {user.id}")
            return
        except Exception as e:
            print(f"  [!] Video send failed for user {user.id}: {e}")

    # Fallback: send text only
    await loading.edit_text(caption, parse_mode=ParseMode.MARKDOWN)

# ─── /me ─────────────────────────────────────────────────────────

async def me_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user(user.id, user.username or user.first_name)
    role = get_user_role(user.id)
    role_label = "👑 Owner" if is_owner(user.id) else (
        "⭐ Premium" if is_premium(user.id) else "🆓 Free"
    )
    today_cnt = get_today_count(user.id)
    limit = "Unlimited" if is_premium(user.id) else FREE_USER_DAILY_LIMIT
    await update.message.reply_text(
        f"📊 **Your Stats**\n\n"
        f"User ID: `{user.id}`\n"
        f"Role: {role_label}\n"
        f"Used today: **{today_cnt}** / {limit}\n"
        f"Total claims: **{get_total_count(user.id)}**\n\n"
        f"Owner: @ankneewayz",
        parse_mode=ParseMode.MARKDOWN,
    )

def get_total_count(user_id: int) -> int:
    conn = get_db()
    cur = conn.execute("SELECT COUNT(*) as cnt FROM email_log WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row["cnt"] if row else 0

# ─── /help ───────────────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔹 **Netflix Trial Bot**\n\n"
        "• `/claim` – Start the trial-offer process\n"
        "• `/me` – See your role, daily usage & total claims\n"
        "• `/help` – This message\n\n"
        "**Free users:** Must join our channel and group. 1 offer per day.\n"
        "**Premium users:** No join required. Unlimited offers.\n\n"
        "**Owner:** @ankneewayz",
        parse_mode=ParseMode.MARKDOWN,
    )

# ─── /claim flow ─────────────────────────────────────────────────

async def claim_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    create_user(user.id, user.username or user.first_name)
    if not is_premium(user.id):
        allowed = await check_membership(update, context)
        if not allowed:
            return ConversationHandler.END
    ok, reason = can_claim_today(user.id)
    if not ok:
        await update.message.reply_text(
            f"❌ **Limit Reached**\n\nYou've used your daily allowance ({reason}).\n"
            f"Come back tomorrow or contact @ankneewayz to upgrade to premium.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END
    await update.message.reply_text(
        "📧 **Send Trial Offer**\n\n"
        "Please reply with the email address you want to send the Netflix trial offer to.\n\n"
        "Example: `user@example.com`\n\n"
        "Type `/cancel` to abort.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return WAITING_EMAIL

async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    email = update.message.text.strip().lower()
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        await update.message.reply_text(
            "❌ **Invalid email.**\nPlease send a valid email address.\n"
            "Example: `user@example.com`\n\n"
            "Type `/cancel` to abort.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return WAITING_EMAIL
    msg = await update.message.reply_text(
        "⏳ **Processing...**\n\n"
        "• Fetching fresh cookies...\n"
        "• Bypassing reCAPTCHA...\n"
        "• Sending trial offer to Netflix...",
        parse_mode=ParseMode.MARKDOWN,
    )
    cookies_dict, cookie_type = fetch_cookies_from_server()
    if not cookies_dict:
        stored = get_active_cookies()
        if stored:
            for s in stored:
                cookies_dict, cookie_type = parse_cookie_content(s["cookie_text"])
                if cookies_dict:
                    break
    if not cookies_dict:
        await msg.edit_text(
            "❌ **Failed**\n\nNo valid cookies available. "
            "Contact @ankneewayz to add fresh cookies.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END
    cookie_string = build_cookie_string(cookies_dict)
    results, success = send_trial_offer(email, cookie_string)
    log_email(
        user.id, email, success,
        json.dumps({"cookie_type": cookie_type, "results": results}),
    )
    if success:
        await msg.edit_text(
            "✅ **Success!**\n\n"
            f"📧 **Email:** `{email}`\n"
            "The Netflix 30-day trial offer has been sent successfully!\n\n"
            "Tell them to check their inbox (and spam folder).\n\n"
            f"Owner: @ankneewayz",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await msg.edit_text(
            "❌ **Failed**\n\n"
            f"📧 **Email:** `{email}`\n"
            "Unable to send the trial offer. This could mean:\n"
            "• Cookies expired – contact @ankneewayz\n"
            "• Netflix blocked the request – try again later\n"
            "• Email already registered\n\n"
            f"Debug: `init={results.get('init', {}).get('status')}`, "
            f"`update={results.get('update', {}).get('status')}`, "
            f"`image={results.get('image', {}).get('status')}`",
            parse_mode=ParseMode.MARKDOWN,
        )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Cancelled. Send `/claim` to start over.",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END

# ═══════════════════════════════════════════════════════════════════
#  OWNER COMMANDS
# ═══════════════════════════════════════════════════════════════════

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Owner only.")
        return
    conn = get_db()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_claims = conn.execute("SELECT COUNT(*) FROM email_log").fetchone()[0]
    success_claims = conn.execute("SELECT COUNT(*) FROM email_log WHERE success=1").fetchone()[0]
    active_cookies = conn.execute("SELECT COUNT(*) FROM cookies WHERE is_active=1").fetchone()[0]
    conn.close()
    await update.message.reply_text(
        "👑 **Owner Panel**\n\n"
        f"**Stats:**\n"
        f"• Total users: `{total_users}`\n"
        f"• Total claims: `{total_claims}`\n"
        f"• Successful: `{success_claims}`\n"
        f"• Active cookies: `{active_cookies}`\n\n"
        "**Commands:**\n"
        "• `/addpremium <user_id>` – Make a user premium\n"
        "• `/removepremium <user_id>` – Demote to free\n"
        "• `/addcookie` – Add a cookie (paste after the command)\n"
        "• `/cookies` – List active cookies\n"
        "• `/broadcast <msg>` – Message all users\n"
        "• `/stats` – Show this panel\n\n"
        "Owner: @ankneewayz",
        parse_mode=ParseMode.MARKDOWN,
    )

async def add_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    try:
        target_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: `/addpremium <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    create_user(target_id)
    set_user_role(target_id, "premium")
    await update.message.reply_text(f"✅ User `{target_id}` is now **Premium**.", parse_mode=ParseMode.MARKDOWN)

async def remove_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    try:
        target_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: `/removepremium <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    create_user(target_id)
    set_user_role(target_id, "free")
    await update.message.reply_text(f"✅ User `{target_id}` is now **Free**.", parse_mode=ParseMode.MARKDOWN)

async def add_cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    text = update.message.text
    cookie_text = text[len("/addcookie"):].strip()
    if not cookie_text:
        await update.message.reply_text(
            "Usage: `/addcookie <cookie_content>`\n\n"
            "Paste your Netflix cookies in JSON or Netscape format after the command.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    parsed, ctype = parse_cookie_content(cookie_text)
    if not parsed:
        await update.message.reply_text(
            "❌ Invalid cookie format. Could not find `NetflixId` or `SecureNetflixId`.\n"
            "Use JSON, Netscape, or simple key=value format.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    save_cookie(cookie_text, ctype or "unknown")
    await update.message.reply_text(
        f"✅ Cookie saved successfully!\n"
        f"Type: `{ctype}`\n"
        f"Keys found: `{', '.join(parsed.keys())}`",
        parse_mode=ParseMode.MARKDOWN,
    )

async def list_cookies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    cookies = get_active_cookies()
    if not cookies:
        await update.message.reply_text("No active cookies in database.", parse_mode=ParseMode.MARKDOWN)
        return
    lines = [f"**Active Cookies ({len(cookies)}):**\n"]
    for c in cookies[:10]:
        preview = c["cookie_text"][:80].replace("\n", " ")
        lines.append(f"• ID `{c['id']}` | Type: `{c['cookie_type']}` | `{preview}...`")
    if len(cookies) > 10:
        lines.append(f"\n... and {len(cookies) - 10} more.")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    text = update.message.text[len("/broadcast"):].strip()
    if not text:
        await update.message.reply_text("Usage: `/broadcast <message>`", parse_mode=ParseMode.MARKDOWN)
        return
    conn = get_db()
    users = conn.execute("SELECT user_id FROM users WHERE is_active=1").fetchall()
    conn.close()
    sent = 0
    failed = 0
    for row in users:
        try:
            await context.bot.send_message(
                chat_id=row["user_id"],
                text=f"📢 **Broadcast**\n\n{text}\n\n— Owner @ankneewayz",
                parse_mode=ParseMode.MARKDOWN,
            )
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(
        f"📨 Broadcast complete.\n• Sent: `{sent}`\n• Failed: `{failed}`",
        parse_mode=ParseMode.MARKDOWN,
    )

# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    claim_conv = ConversationHandler(
        entry_points=[CommandHandler("claim", claim_start)],
        states={
            WAITING_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("me", me_command))
    app.add_handler(claim_conv)
    app.add_handler(CommandHandler("stats", owner_panel))
    app.add_handler(CommandHandler("addpremium", add_premium))
    app.add_handler(CommandHandler("removepremium", remove_premium))
    app.add_handler(CommandHandler("addcookie", add_cookie))
    app.add_handler(CommandHandler("cookies", list_cookies))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(check_membership_callback, pattern="^check_membership$"))

    print(f"🤖 Bot started. Owner: @ankneewayz")
    print(f"📢 Required channel: {REQUIRED_CHANNEL}")
    print(f"💬 Required group:   {REQUIRED_GROUP}")
    print(f"📌 Pinterest pin:    {PINTEREST_PIN_URL}")
    print("Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()