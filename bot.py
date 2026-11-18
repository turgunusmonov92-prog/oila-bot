"""Kuniga 3 marta (07:00, 12:00, 19:00) guruhga oila haqida buyuk mutafakkirlar iqtibosini yuboradigan Telegram bot.

Ishlatish:
    python bot.py            # bugungi iqtibosni guruhga yuboradi
    python bot.py --dry-run  # yubormasdan, xabar matnini ekranga chiqaradi

Kerakli muhit o'zgaruvchilari (GitHub Secrets):
    BOT_TOKEN - @BotFather bergan token
    CHAT_ID   - guruh ID raqami (masalan: -1001234567890)
"""
import datetime
import html
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from quotes import QUOTES

TASHKENT = datetime.timezone(datetime.timedelta(hours=5))
START = datetime.date(2026, 11, 18)  # 1-iqtibos shu kuni yuboriladi

OYLAR = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul",
         "avgust", "sentyabr", "oktyabr", "noyabr", "dekabr"]
KUNLAR = ["dushanba", "seshanba", "chorshanba", "payshanba", "juma", "shanba", "yakshanba"]
YAKUN = [
    "Oilangizga mehr ulashing! 🌷",
    "Bugun yaqinlaringizga bir iliq so'z ayting. 🤍",
    "Ota-onangizdan hol so'rashni unutmang. 🌿",
    "Oila - eng katta boylik. 🏡",
    "Farzandlaringiz bilan bugun 10 daqiqa suhbatlashing. 🌱",
    "Kuningiz barakali, uyingiz tinch bo'lsin! ☀️",
    "Mehr - oilaning poydevori. 💛",
]


def esc(s):
    return html.escape(s, quote=False)


def current_slot(now=None):
    """0 - ertalab (07:00), 1 - tush (12:00), 2 - kechqurun (19:00)."""
    now = now or datetime.datetime.now(TASHKENT)
    if now.hour < 10:
        return 0
    if now.hour < 16:
        return 1
    return 2


def todays_message(today=None, slot=None):
    now = datetime.datetime.now(TASHKENT)
    today = today or now.date()
    slot = current_slot(now) if slot is None else slot
    day = (today - START).days
    # Kuniga 3 ta iqtibos. 18-noyabr ertalab 1-iqtibos chiqqan, kechqurun 2-iqtibos.
    idx = (day * 3 + slot - 1) % len(QUOTES)
    text, author, source, mazmunan = QUOTES[idx]
    num = idx + 1
    sana = f"{today.day}-{OYLAR[today.month - 1]}, {KUNLAR[today.weekday()]}"
    note = " (mazmunan)" if mazmunan else ""
    return (
        f"👨‍👩‍👧‍👦 <b>Oila haqida kun hikmati</b> · {esc(sana)}\n\n"
        f"<i>«{esc(text)}»</i>\n\n"
        f"— <b>{esc(author)}</b>\n"
        f"📖 {esc(source)}{note}\n\n"
        f"{YAKUN[idx % len(YAKUN)]}\n"
        f"<code>#{num}/{len(QUOTES)}</code>"
    )


def show_chats(token):
    """Bot qaysi guruhlarni ko'rganini chiqaradi (CHAT_ID'ni aniqlash uchun)."""
    try:
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getMe", timeout=30) as r:
            me = json.load(r).get("result", {})
        print("Token qaysi botniki:", "@" + str(me.get("username")))
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        with urllib.request.urlopen(url, timeout=30) as r:
            res = json.load(r)
        seen = {}
        for u in res.get("result", []):
            for k in ("message", "my_chat_member", "chat_member", "edited_message"):
                c = (u.get(k) or {}).get("chat")
                if c:
                    seen[c["id"]] = c.get("title") or c.get("username")
        print("Bot ko'rgan chatlar (CHAT_ID: nomi):", seen)
    except Exception as e:  # faqat yordamchi ma'lumot
        print("Chatlar ro'yxatini olib bo'lmadi:", e)


def send(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        print("Telegram javobi:", e.read().decode(errors="replace"))
        show_chats(token)
        raise SystemExit(1)
    if not res.get("ok"):
        raise SystemExit(f"Telegram xatosi: {res}")
    print("Yuborildi ✅")


if __name__ == "__main__":
    msg = todays_message()
    if "--dry-run" in sys.argv:
        print(msg)
        sys.exit()
    # Nusxalashda tasodifan qo'shilgan bo'sh joy va qator ko'chishlarini olib tashlaymiz
    token = "".join((os.environ.get("BOT_TOKEN") or "").split())
    chat_id = "".join((os.environ.get("CHAT_ID") or "").split())
    if not token or not chat_id:
        raise SystemExit("BOT_TOKEN va CHAT_ID o'rnatilmagan.")
    send(token, chat_id, msg)
