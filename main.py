from flask import Flask, request
import os, requests, threading, time

app = Flask(__name__)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = "YOUR_CHANNEL_ID"
MESSAGE_ID = "YOUR_MESSAGE_ID"
TIMEOUT_SECONDS = 300  # 5 minutes

# Store user heartbeats {user_id: last_seen_timestamp}
user_heartbeats = {}

def update_discord_message():
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages/{MESSAGE_ID}"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    count = len(user_heartbeats)
    json = {"content": f"🟢 Online Users: **{count}**"}
    requests.patch(url, headers=headers, json=json)

@app.route("/webhook", methods=["POST"])
def receive_ping():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return {"error": "Missing user_id"}, 400

    user_heartbeats[user_id] = time.time()
    update_discord_message()

    return {"message": f"Heartbeat received from {user_id}", "online": len(user_heartbeats)}, 200

def cleanup_thread():
    while True:
        time.sleep(60)  # check every minute
        now = time.time()
        removed = []

        for user_id in list(user_heartbeats):
            if now - user_heartbeats[user_id] > TIMEOUT_SECONDS:
                removed.append(user_id)
                del user_heartbeats[user_id]

        if removed:
            update_discord_message()

# Start background cleanup thread
threading.Thread(target=cleanup_thread, daemon=True).start()

@app.route("/")
def index():
    return "Heartbeat listener is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
