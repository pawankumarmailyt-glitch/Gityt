import requests
import json
import time
import os

# ========== CONFIG ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_USERNAME = "@plus_official01"
CHANNEL_LINK = "https://t.me/plus_official01"
BOT_USERNAME = "numbertoinffo1_bot"

ADMIN_ID = 8351165824

SHORTNER_API = "https://arolinks.com/api"
SHORTNER_KEY = os.getenv("SHORTNER_KEY")

API_URL = "https://yash-code-with-ai.alphamovies.workers.dev/?key=7189814021&num="

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

verified_users = {}

# ========== TELEGRAM FUNCTIONS ==========
def get_updates(offset=None):
    url = BASE_URL + "getUpdates?timeout=100"
    if offset:
        url += f"&offset={offset}"
    try:
        return requests.get(url).json()
    except:
        return {}

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
    except:
        pass

# ========== JOIN CHECK ==========
def check_join(user_id):
    url = BASE_URL + f"getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
    try:
        res = requests.get(url).json()
        if res.get("ok"):
            return res["result"]["status"] in ["member", "administrator", "creator"]
    except:
        pass
    return False

# ========== SHORT LINK ==========
def create_link(user_id):
    deep_link = f"https://t.me/{numbertoinffo1_bot}?start=verify_{user_id}"
    url = f"{SHORTNER_API}?api={SHORTNER_KEY}&url={deep_link}"
    try:
        res = requests.get(url).json()
        return res.get("shortenedUrl")
    except:
        return None

# ========== PREMIUM FORMAT ==========
def format_data(data):
    try:
        name = data.get("name", "N/A")
        number = data.get("mobile", "N/A")
        father = data.get("father_name", "N/A")
        city = data.get("city", "N/A")
        address = data.get("address", "N/A")
        email = data.get("email", "N/A")

        return f"""
╔═══════ 🔍 *PREMIUM NUMBER INFO* ═══════╗

👤 *NAME*  
➤ `{name}`

📱 *NUMBER*  
➤ `{number}`

👨‍👦 *FATHER NAME*  
➤ `{father}`

🌆 *CITY*  
➤ `{city}`

🏠 *ADDRESS*  
➤ `{address}`

📧 *EMAIL*  
➤ `{email}`

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
    except:
        return None

# ========== HANDLER ==========
def handle(chat_id, text):

    # START
    if text.startswith("/start"):

        # VERIFY RETURN
        if "verify_" in text:
            uid = text.split("_")[1]
            if str(chat_id) == uid:
                verified_users[chat_id] = True
                send_message(chat_id, "✅ Verification Successful!\n\nअब /num use करो")
                return

        # FORCE JOIN
        if not check_join(chat_id):
            btn = {
                "inline_keyboard": [
                    [{"text": "📢 Join Channel", "url": CHANNEL_LINK}]
                ]
            }
            send_message(chat_id, "🚫 पहले channel join करो", btn)
            return

        # VERIFY LINK
        link = create_link(chat_id)

        if not link:
            send_message(chat_id, "❌ Short link error, try again")
            return

        btn = {
            "inline_keyboard": [
                [{"text": "🔗 Verify Now", "url": link}]
            ]
        }

        send_message(chat_id, "⚠️ Access Unlock करने के लिए verify करो", btn)

    # HELP
    elif text == "/help":
        send_message(chat_id,
        "📌 Commands:\n/start\n/help\n/num 9876543210")

    # NUMBER
    elif text.startswith("/num"):

        if not verified_users.get(chat_id):
            send_message(chat_id, "❌ पहले /start करके verify करो")
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

    # ADMIN USERS
    elif text == "/users":
        if chat_id == ADMIN_ID:
            send_message(chat_id, "👑 Bot is running fine!")

    else:
        send_message(chat_id, "❌ Unknown command")

# ========== MAIN ==========
def main():
    last_update = None
    print("🤖 BOT STARTED SUCCESSFULLY")

    while True:
        updates = get_updates(last_update)

        if "result" in updates:
            for update in updates["result"]:
                last_update = update["update_id"] + 1

                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text")

                    if text:
                        handle(chat_id, text)

        time.sleep(2)

# ========== RUN ==========
if __name__ == "__main__":
    main()
