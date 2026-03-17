import requests
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ================= CONFIG =================
BOT_TOKEN = "8633522224:AAHK62_S-flLwbZii5f-tJ4OQcw_zI5qoeA"
BOT_USERNAME = "numtoinffo_bot"

CHANNEL_1 = "@plus_official01"
CHANNEL_2 = "@cinestream01"

CHANNEL_LINK_1 = "https://t.me/plus_official01"
CHANNEL_LINK_2 = "https://t.me/cinestream01"

DATABASE_CHANNEL = -1003525179083

EXTERNAL_API_URL = "https://nv2.ek4nsh.in/api?key=3012&mobile="

SHORTNER_API = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_URL = "https://arolinks.com"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ================= STORAGE =================
joined_users = set()
verified_users = {}
search_verified = {}

# ================= WEB SERVER =================
def run_web():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot Running 🚀")

    server = HTTPServer(("0.0.0.0", 10000), Handler)
    print("🌐 Web server running on port 10000")
    server.serve_forever()

# ================= BASIC =================
def send_message(chat_id, text, buttons=None):
    try:
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        if buttons:
            data["reply_markup"] = buttons

        requests.post(BASE_URL + "sendMessage", json=data, timeout=10)
    except Exception as e:
        print("Send Message Error:", e)

# ================= JOIN CHECK =================
def check_join(user_id):
    try:
        r1 = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": CHANNEL_1,
            "user_id": user_id
        }, timeout=10).json()

        r2 = requests.get(BASE_URL + "getChatMember", params={
            "chat_id": CHANNEL_2,
            "user_id": user_id
        }, timeout=10).json()

        s1 = r1["result"]["status"]
        s2 = r2["result"]["status"]

        return s1 in ["member","administrator","creator"] and s2 in ["member","administrator","creator"]
    except Exception as e:
        print("Join Check Error:", e)
        return False

# ================= SHORTNER =================
def short_link(user_id):
    try:
        link = f"https://t.me/{numtoinffo_bot}?start=search_{user_id}"
        api = f"{SHORTNER_URL}/api?api={SHORTNER_API}&url={link}"

        res = requests.get(api, timeout=10).json()

        if res.get("status") == "success":
            return res["shortenedUrl"]

        return link
    except Exception as e:
        print("Shortner Error:", e)
        return link

# ================= FORMAT =================
def format_data(data):
    try:
        data = data.get("data", data)
    except:
        data = {}

    return f"""
📊 RESULT HERE

👤 Name: {data.get("name","Not Found")}
👨 Father: {data.get("father_name","Not Found")}
📶 Carrier: {data.get("carrier","Not Found")}
🏙️ City: {data.get("city","Not Found")}
🏠 Address: {data.get("address","Not Found")}
📱 Second Number: {data.get("secondary_number","Not Found")}
📧 Gmail: {data.get("email","Not Found")}
"""

# ================= CALLBACK =================
def answer_callback(cid):
    try:
        requests.post(BASE_URL + "answerCallbackQuery", data={
            "callback_query_id": cid
        }, timeout=10)
    except:
        pass

# ================= BOT =================
def run_bot():
    print("🤖 Bot Started...")
    offset = 0

    while True:
        try:
            res = requests.get(
                BASE_URL + "getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35
            ).json()

            for upd in res.get("result", []):
                offset = upd["update_id"] + 1

                # ===== CALLBACK =====
                if "callback_query" in upd:
                    cb = upd["callback_query"]
                    user_id = cb["from"]["id"]
                    chat_id = cb["message"]["chat"]["id"]
                    data = cb["data"]

                    answer_callback(cb["id"])

                    if data == "check_join":
                        if check_join(user_id):
                            joined_users.add(user_id)

                            buttons = {
                                "inline_keyboard":[
                                    [{"text":"✅ Verify Now","callback_data":"verify_simple"}]
                                ]
                            }

                            send_message(chat_id,
                            "🎉 Thank you for joining ❤️\n\nअब verify कर लो 👇",
                            buttons)
                        else:
                            send_message(chat_id,"❌ Please join both channels first 😢")

                    elif data == "verify_simple":
                        verified_users[user_id] = True
                        send_message(chat_id,"✅ Verified!\n\n📱 अब 10 digit number भेजो")

                    continue

                if "message" not in upd:
                    continue

                msg = upd["message"]
                chat_id = msg["chat"]["id"]
                user_id = msg["from"]["id"]
                text = msg.get("text","")

                # ===== START =====
                if text.startswith("/start"):

                    if "search_" in text:
                        search_verified[user_id] = True
                        send_message(chat_id,"✅ Verification done! अब result देखो 👇")
                        continue

                    if not check_join(user_id):
                        buttons = {
                            "inline_keyboard":[
                                [{"text":"📢 Join Channel 1","url":CHANNEL_LINK_1}],
                                [{"text":"📢 Join Channel 2","url":CHANNEL_LINK_2}],
                                [{"text":"💖 मैंने Join कर लिया","callback_data":"check_join"}]
                            ]
                        }

                        send_message(chat_id,
                        "👋 Hello dear ❤️\n\n"
                        "थोड़ा support कर दो 🙏\n"
                        "नीचे दिए गए दोनों channel join कर लो\n"
                        "फिर आगे बढ़ सकते हो 🚀",
                        buttons)
                        continue

                    send_message(chat_id,"🔐 Verify करो 👇")
                    continue

                # ===== NUMBER =====
                if text.isdigit() and len(text) == 10:

                    if user_id not in verified_users:
                        send_message(chat_id,"❌ पहले verify करो")
                        continue

                    if user_id not in search_verified:
                        send_message(chat_id,
                        f"🔐 Details देखने के लिए verify करो 👇\n{short_link(user_id)}")
                        continue

                    try:
                        data = requests.get(EXTERNAL_API_URL + text, timeout=15).json()
                        result = format_data(data)

                        send_message(chat_id, result)

                        send_message(
                            DATABASE_CHANNEL,
                            f"📥 User: {user_id}\n📱 Number: {text}\n{result}"
                        )

                        # reset
                        search_verified.pop(user_id, None)

                    except Exception as e:
                        print("API Error:", e)
                        send_message(chat_id,"❌ API Error try again")

                else:
                    send_message(chat_id,"❌ सही 10 digit number भेजो")

        except Exception as e:
            print("MAIN LOOP ERROR:", e)
            time.sleep(5)

# ================= RUN =================
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
