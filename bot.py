import requests
import json
import time

# ================= CONFIG =================
BOT_TOKEN = "8633522224:AAHK62_S-flLwbZii5f-tJ4OQcw_zI5qoeA"
EXTERNAL_API_URL = "https://nv2.ek4nsh.in/api?key=3012&mobile=9876543210"
SHORTNER_URL = "https://arolinks.com/api"
SHORTNER_API = "70a4cdbd945a01d2be1459bef097f66fd742508b"
ADMIN_ID = 8351165824

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ================= STORAGE =================
user_states = {}
verified_users = {}
daily_stats = {}

# ================= FUNCTIONS =================

def send_message(chat_id, text, reply_markup=None):
    url = BASE_URL + "sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    requests.post(url, data=payload)


def get_updates(offset):
    url = BASE_URL + "getUpdates"
    params = {"timeout": 30, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()


def create_keyboard():
    return {
        "keyboard": [["📱 Phone Lookup"]],
        "resize_keyboard": True
    }


def is_verified(user_id):
    if user_id in verified_users:
        if time.time() < verified_users[user_id]:
            return True
    return False


def generate_verification_link(user_id):
    long_url = f"https://t.me/?start=verify_{user_id}"

    if SHORTNER_API and SHORTNER_URL:
        try:
            api = f"{SHORTNER_URL}/api?api={SHORTNER_API}&url={long_url}"
            r = requests.get(api).json()
            return r.get("shortenedUrl", long_url)
        except:
            return long_url
    return long_url


def verify_user(user_id):
    verified_users[user_id] = time.time() + (12 * 60 * 60)

    today = time.strftime("%Y-%m-%d")
    if today not in daily_stats:
        daily_stats[today] = set()

    daily_stats[today].add(user_id)


def send_daily_report():
    today = time.strftime("%Y-%m-%d")
    if today in daily_stats:
        count = len(daily_stats[today])
        send_message(ADMIN_ID, f"📊 Daily Verification Completed: {count}")
        daily_stats[today] = set()


# ================= MAIN LOOP =================

def main():
    offset = 0
    last_report_day = time.strftime("%d")

    while True:
        data = get_updates(offset)

        if data.get("ok"):
            for update in data["result"]:
                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]
                chat_id = message["chat"]["id"]
                user_id = message["from"]["id"]
                text = message.get("text", "")

                # ===== START =====
                if text == "/start":
                    send_message(
                        chat_id,
                        "👋 Welcome!\nUse the button below:",
                        create_keyboard()
                    )
                    continue

                # ===== ADMIN COMMANDS =====
                if user_id == ADMIN_ID:
                    if text.startswith("/setshortner"):
                        try:
                            parts = text.split()
                            global SHORTNER_API, SHORTNER_URL
                            SHORTNER_API = parts[1]
                            SHORTNER_URL = parts[2]
                            send_message(chat_id, "✅ Shortner set globally!")
                        except:
                            send_message(chat_id, "❌ Usage:\n/setshortner API URL")
                        continue

                # ===== VERIFY CHECK =====
                if not is_verified(user_id):
                    link = generate_verification_link(user_id)
                    send_message(
                        chat_id,
                        f"🔒 You need to verify first.\n\nComplete task:\n{link}"
                    )
                    continue

                # ===== BUTTON =====
                if text == "📱 Phone Lookup":
                    user_states[user_id] = "WAITING_NUMBER"
                    send_message(chat_id, "📞 Send 10 digit mobile number:")
                    continue

                # ===== NUMBER INPUT =====
                if user_states.get(user_id) == "WAITING_NUMBER":

                    if text.isdigit() and len(text) == 10:
                        try:
                            api_url = EXTERNAL_API_URL + text
                            r = requests.get(api_url)
                            data = r.json()

                            formatted = json.dumps(data, indent=2)

                            send_message(
                                chat_id,
                                f"<pre>{formatted}</pre>\n\n"
                                f"🔔 Subscribe for more:\n"
                                f"https://t.me/plus_official01"
                            )

                        except:
                            send_message(chat_id, "❌ API Error")

                    else:
                        send_message(chat_id, "❌ Invalid number. Send 10 digits only.")

                    user_states[user_id] = None

        # ===== DAILY REPORT =====
        current_day = time.strftime("%d")
        if current_day != last_report_day:
            send_daily_report()
            last_report_day = current_day

        time.sleep(2)


# ================= RUN =================
if __name__ == "__main__":
    main()
