import requests
import json
import time

BOT_TOKEN = ""  # apna bot token daalo
API_URL = "https://nv2.ek4nsh.in/api?key=3012&mobile="
SHORTNER_API = "https://arolinks.com/api?api=YOUR_API_KEY&url="

CHANNELS = ["@plus_official01", "@cinestream01"]

users = {}
verified_users = {}

# ================== SEND MESSAGE ==================
def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    requests.post(url, data=data)

# ================== CHECK JOIN ==================
def is_joined(user_id):
    for ch in CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={ch}&user_id={user_id}"
        res = requests.get(url).json()
        if res["result"]["status"] not in ["member", "administrator", "creator"]:
            return False
    return True

# ================== SHORT LINK ==================
def get_short_link(user_id):
    verify_url = f"https://t.me/numtoinffo_bot?start=verify_{user_id}"
    short = requests.get(SHORTNER_API + verify_url).json()
    return short.get("shortenedUrl", verify_url)

# ================== MAIN ==================
def main():
    offset = 0

    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            res = requests.get(url, params={"offset": offset, "timeout": 10}).json()

            for update in res["result"]:
                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                msg = update["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")

                # ===== START =====
                if text.startswith("/start"):
                    users[user_id] = {"step": "start"}

                    keyboard = {
                        "keyboard": [["🚀 Start Using Bot"]],
                        "resize_keyboard": True
                    }

                    send_message(chat_id,
                        "👋 <b>Welcome Dost ❤️</b>\n\n"
                        "✨ Yeh bot aapko number details deta hai\n"
                        "🔐 Use karne ke liye pehle verify karna hoga",
                        keyboard)

                # ===== START USING BOT =====
                elif text == "🚀 Start Using Bot":
                    if not is_joined(user_id):
                        keyboard = {
                            "inline_keyboard": [
                                [{"text": "📢 Channel 1", "url": "https://t.me/plus_official01"}],
                                [{"text": "📢 Channel 2", "url": "https://t.me/cinestream01"}],
                                [{"text": "✅ Verify", "callback_data": "verify"}]
                            ]
                        }

                        send_message(chat_id,
                            "🥺 <b>Dost please pehle hamare channels join kar lo</b>\n\n"
                            "💖 Aapka support bahut important hai\n"
                            "👇 Join karke VERIFY button dabao",
                            keyboard)
                        continue

                    short_link = get_short_link(user_id)

                    send_message(chat_id,
                        f"🔐 <b>Verification Required</b>\n\n"
                        f"👉 Please verify here:\n{short_link}\n\n"
                        f"💖 Sirf 1 step hai dost",
                    )

                    verified_users[user_id] = False

                # ===== VERIFY COMPLETE =====
                elif "verify_" in text:
                    verified_users[user_id] = True

                    keyboard = {
                        "keyboard": [["📱 Phone Lookup"]],
                        "resize_keyboard": True
                    }

                    send_message(chat_id,
                        "✅ <b>Verification Complete 🎉</b>\n\n"
                        "📱 Ab number search kar sakte ho",
                        keyboard)

                # ===== PHONE LOOKUP BUTTON =====
                elif text == "📱 Phone Lookup":
                    if not verified_users.get(user_id, False):
                        send_message(chat_id, "⚠️ Pehle verify karo")
                        continue

                    users[user_id]["step"] = "waiting_number"
                    send_message(chat_id, "📞 10 digit number bhejo:")

                # ===== NUMBER INPUT =====
                elif text.isdigit() and len(text) == 10:
                    if users.get(user_id, {}).get("step") != "waiting_number":
                        continue

                    if not verified_users.get(user_id, False):
                        send_message(chat_id, "⚠️ Pehle verify karo")
                        continue

                    send_message(chat_id, "🔍 Searching...")

                    api = requests.get(API_URL + text, timeout=10).json()

                    formatted = json.dumps(api, indent=2)

                    send_message(chat_id,
                        f"<pre>{formatted}</pre>\n\n"
                        "🔔 More tools: https://t.me/pluso_official01"
                    )

                else:
                    send_message(chat_id, "❌ Invalid input")

        except Exception as e:
            print("Error:", e)
            time.sleep(5)

# ================== RUN ==================
while True:
    try:
        main()
    except Exception as e:
        print("Crash:", e)
        time.sleep(5)
