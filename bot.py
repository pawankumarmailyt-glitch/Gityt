import requests
import json
import os
from flask import Flask, request

# ========== CONFIG ==========
BOT_TOKEN = os.getenv("8659209680:AAF0PFICCemksGbnoFk_DgEqNhGsGlDhBiU")
SHORTNER_KEY = os.getenv("70a4cdbd945a01d2be1459bef097f66fd742508b")

CHANNEL_USERNAME = "@plus_official01"
CHANNEL_LINK = "https://t.me/plus_official01"
BOT_USERNAME = "numbertoinffo1_bot"

ADMIN_ID = 8351165824

SHORTNER_API = "https://arolinks.com/api"
API_URL = "https://yash-code-with-ai.alphamovies.workers.dev/?key=7189814021&num="

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

verified_users = {}

app = Flask(__name__)

# ========== TELEGRAM SEND ==========
def send_message(chat_id, text, buttons=None):
    url = BASE_URL + "sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    if buttons:
        data["reply_markup"] = json.dumps(buttons)

    try:
        requests.post(url, data=data)
    except Exception as e:
        print("SEND ERROR:", e)

# ========== JOIN CHECK ==========
def check_join(user_id):
    url = BASE_URL + f"getChatMember?chat_id={plus_official01}&user_id={user_id}"
    try:
        res = requests.get(url).json()
        if res.get("ok"):
            return res["result"]["status"] in ["member", "administrator", "creator"]
    except Exception as e:
        print("JOIN ERROR:", e)
    return False

# ========== SHORT LINK ==========
def create_link(user_id):
    deep_link = f"https://t.me/{numbertoinffo1_bot}?start=verify_{user_id}"
    url = f"{SHORTNER_API}?api={SHORTNER_KEY}&url={deep_link}"
    try:
        res = requests.get(url).json()
        return res.get("shortenedUrl")
    except Exception as e:
        print("SHORTNER ERROR:", e)
        return None

# ========== FORMAT ==========
def format_data(data):
    try:
        return f"""
╔═══════ 🔍 *PREMIUM NUMBER INFO* ═══════╗

👤 *NAME*  
➤ `{data.get("name", "N/A")}`

📱 *NUMBER*  
➤ `{data.get("mobile", "N/A")}`

👨‍👦 *FATHER NAME*  
➤ `{data.get("father_name", "N/A")}`

🌆 *CITY*  
➤ `{data.get("city", "N/A")}`

🏠 *ADDRESS*  
➤ `{data.get("address", "N/A")}`

📧 *EMAIL*  
➤ `{data.get("email", "N/A")}`

╚═══════════════════════════════╝

⚡ Powered by @{BOT_USERNAME}
"""
    except:
        return "❌ Data formatting error"

# ========== API ==========
def get_number_info(num):
    try:
        res = requests.get(API_URL + num)
        return res.json()
    except Exception as e:
        print("API ERROR:", e)
        return None

# ========== HANDLER ==========
def handle(chat_id, text):

    if text.startswith("/start"):

        if "verify_" in text:
            uid = text.split("_")[1]
            if str(chat_id) == uid:
                verified_users[chat_id] = True
                send_message(chat_id, "✅ Verification Successful!\n\nअब /num use करो")
                return

        if not check_join(chat_id):
            btn = {
                "inline_keyboard": [
                    [{"text": "📢 Join Channel", "url": CHANNEL_LINK}]
                ]
            }
            send_message(chat_id, "🚫 पहले channel join करो", btn)
            return

        link = create_link(chat_id)

        if not link:
            send_message(chat_id, "❌ Short link error")
            return

        btn = {
            "inline_keyboard": [
                [{"text": "🔗 Verify Now", "url": link}]
            ]
        }

        send_message(chat_id, "⚠️ Access Unlock करने के लिए verify करो", btn)

    elif text == "/help":
        send_message(chat_id, "📌 Commands:\n/start\n/help\n/num 9876543210")

    elif text.startswith("/num"):

        if not verified_users.get(chat_id):
            send_message(chat_id, "❌ पहले verify करो (/start)")
            return

        parts = text.split()
        if len(parts) != 2:
            send_message(chat_id, "❌ सही format:\n/num 9876543210")
            return

        num = parts[1]
        send_message(chat_id, "🔍 Data fetch हो रहा है...")

        data = get_number_info(num)

        if not data:
            send_message(chat_id, "❌ API Error")
            return

        send_message(chat_id, format_data(data))

    elif text == "/users":
        if chat_id == ADMIN_ID:
            send_message(chat_id, f"👑 Total Users: {len(verified_users)}")

    else:
        send_message(chat_id, "❌ Unknown command")

# ========== WEBHOOK ==========
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("UPDATE:", data)

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text")

            if text:
                handle(chat_id, text)

    except Exception as e:
        print("WEBHOOK ERROR:", e)

    return "ok"

# ========== RUN ==========
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
