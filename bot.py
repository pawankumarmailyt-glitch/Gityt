import requests
import json
import time
import os

# ========== CONFIG ==========
BOT_TOKEN = "8659209680:AAF0PFICCemksGbnoFk_DgEqNhGsGlDhBiU"

CHANNEL_USERNAME = "@plus_official01"
CHANNEL_LINK = "https://t.me/plus_official01"

BOT_USERNAME = "numbertoinffo1_bot"

ADMIN_ID = 8351165824  # अपना telegram id डालो

SHORTNER_API = "https://arolinks.com/api"
SHORTNER_KEY = "70a4cdbd945a01d2be1459bef097f66fd742508b"

API_URL = "https://yash-code-with-ai.alphamovies.workers.dev/?key=7189814021&num="

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ========== DATABASE ==========
USER_FILE = "users.txt"

def save_user(user_id):
    if not os.path.exists(USER_FILE):
        open(USER_FILE, "w").close()

    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()

    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(str(user_id) + "\n")

def get_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return f.read().splitlines()


verified = {}

# ========== TELEGRAM ==========
def get_updates(offset=None):
    url = BASE_URL + "getUpdates?timeout=100"
    if offset:
        url += f"&offset={offset}"
    return requests.get(url).json()

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

    requests.post(url, data=data)

def send_broadcast(text):
    users = get_users()
    for user in users:
        try:
            send_message(user, text)
            time.sleep(0.1)
        except:
            pass

# ========== JOIN CHECK ==========
def check_join(user_id):
    url = BASE_URL + f"getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
    res = requests.get(url).json()
    if res["ok"]:
        return res["result"]["status"] in ["member", "administrator", "creator"]
    return False

# ========== SHORT LINK ==========
def create_link(user_id):
    deep = f"https://t.me/{numbertoinffo1_bot}?start=verify_{user_id}"
    url = f"{SHORTNER_API}?api={SHORTNER_KEY}&url={deep}"
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

        msg = f"""
╔═══════ 🔍 * NUMBER   INFO* ═══════╗

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

📧 *GMAIL / EMAIL*  
➤ `{email}`

╚═══════════════════════════════╝

⚡ Powered by @{plus_official01}
"""
        return msg

    except:
        return "❌ Error formatting data"

# ========== API ==========
def get_info(num):
    try:
        return requests.get(API_URL + num).json()
    except:
        return None

# ========== HANDLER ==========
def handle(chat_id, text):

    save_user(chat_id)

    # START
    if text.startswith("/start"):

        if "verify_" in text:
            uid = text.split("_")[1]
            if str(chat_id) == uid:
                verified[chat_id] = True
                send_message(chat_id, "✅ Verification Successful!\n\nअब आप /num use कर सकते हो")
                return

        if not check_join(chat_id):
            btn = {
                "inline_keyboard": [
                    [{"text": "📢 Join Channel", "url": CHANNEL_LINK}],
                    [{"text": "🔄 Check Again", "callback_data": "check"}]
                ]
            }
            send_message(chat_id, "🚫 पहले channel join करो फिर verify करो", btn)
            return

        link = create_link(chat_id)

        btn = {
            "inline_keyboard": [
                [{"text": "🔗 Verify Now", "url": link}]
            ]
        }

        send_message(chat_id, "⚠️ Access Unlock करने के लिए verify करो", btn)

    # HELP
    elif text == "/help":
        send_message(chat_id,
        "📌 *Commands*\n\n"
        "/start - Start bot\n"
        "/help - Help\n"
        "/num 9876543210 - Get number info")

    # NUMBER
    elif text.startswith("/num"):

        if not verified.get(chat_id):
            send_message(chat_id, "❌ पहले /start करके verify करो")
            return

        parts = text.split()
        if len(parts) != 2:
            send_message(chat_id, "❌ सही format:\n/num 9876543210")
            return

        num = parts[1]

        send_message(chat_id, "🔍 Data fetch हो रहा है...")

        data = get_info(num)

        if not data:
            send_message(chat_id, "❌ API Error")
            return

        send_message(chat_id, format_data(data))

    # ADMIN BROADCAST
    elif text.startswith("/broadcast"):
        if chat_id != ADMIN_ID:
            return

        msg = text.replace("/broadcast ", "")
        send_broadcast(msg)
        send_message(chat_id, "✅ Broadcast Sent")

    # USER COUNT
    elif text == "/users":
        if chat_id == ADMIN_ID:
            send_message(chat_id, f"👥 Total Users: {len(get_users())}")

    else:
        send_message(chat_id, "❌ Unknown command")

# ========== MAIN ==========
def main():
    last = None
    print("🤖 BOT STARTED...")

    while True:
        updates = get_updates(last)

        if "result" in updates:
            for u in updates["result"]:
                last = u["update_id"] + 1

                if "message" in u:
                    chat_id = u["message"]["chat"]["id"]
                    text = u["message"].get("text")

                    if text:
                        handle(chat_id, text)

        time.sleep(2)

if __name__ == "__main__":
    main(){}).get("step") != "wait_number":
                        continue

                    if not verified_users.get(user_id, False):
                        send_message(chat_id, "⚠️ Pehle verify karo")
                        continue

                    send_message(chat_id, "🔍 Searching...")

                    try:
                        api = requests.get(API_URL + text, timeout=10).json()
                        formatted = json.dumps(api, indent=2)

                        send_message(chat_id,
                            f"<pre>{formatted}</pre>\n\n"
                            "🔔 More tools: https://t.me/pluso_official01"
                        )
                    except:
                        send_message(chat_id, "❌ API Error")

                else:
                    send_message(chat_id, "❌ Invalid input")

        except Exception as e:
            print("Error:", e)
            time.sleep(5)

# ================= RUN =================
while True:
    try:
        main()
    except Exception as e:
        print("Crash:", e)
        time.sleep(5)
