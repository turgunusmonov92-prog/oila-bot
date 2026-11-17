"""Har kuni guruhga oila haqida buyuk mutafakkirlar iqtibosini yuboradigan Telegram bot.

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


def todays_message(today=None):
    today = today or datetime.datetime.now(TASHKENT).date()
    day = (today - START).days
    text, author, source, mazmunan = QUOTES[day % len(QUOTES)]
    num = day % len(QUOTES) + 1
    sana = f"{today.day}-{OYLAR[today.month - 1]}, {KUNLAR[today.weekday()]}"
    note = " (mazmunan)" if mazmunan else ""
    return (
        f"👨‍👩‍👧‍👦 <b>Oila haqida kun hikmati</b> · {esc(sana)}\n\n"
        f"<i>«{esc(text)}»</i>\n\n"
        f"— <b>{esc(author)}</b>\n"
        f"📖 {esc(source)}{note}\n\n"
        f"{YAKUN[day % len(YAKUN)]}\n"
        f"<code>#{num}/{len(QUOTES)}</code>"
    )


def send(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as r:
        res = json.load(r)
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
