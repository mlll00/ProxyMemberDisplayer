from flask import Flask, request
import os
import requests
import threading
import time

app = Flask(__name__)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = "1359275211500814447"  # Replace with your actual channel ID
MESSAGE_ID = "1359292187396931636"  # Replace with your actual message ID
TIMEOUT_SECONDS = 30  # 30 Seconds timeout for inactive users

# Store user heartbeats {user_id: last_seen_timestamp}
user_heartbeats = {}

def update_discord_message():
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages/{MESSAGE_ID}"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    count = len(user_heartbeats)
    
    # Create an embed
    embed = {
        "title": "Proxy User Status",
        "description": "Real-time user activity tracking",
        "color": 0x5865F2,  # Discord blurple color
        "fields": [
            {
                "name": "Online Users",
                "value": f"```\n{count} active connections\n```",
                "inline": True
            },
            {
                "name": "Last Updated",
                "value": f"<t:{int(time.time())}:R>",
                "inline": True
            }
        ],
        "footer": {
            "text": "User Status Logger",
            "icon_url": "https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6a49cf127bf92de1e2_icon_clyde_blurple_RGB.png"
        },
        "thumbnail": {
            "url": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnhyanp1MXJ5Y2hnZDFhOTQ5eW5zaWtkOXI3NzRxejczOHFrOTR4dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/J47crA9L0GpTBsLMVK/giphy.gif"
        },
        "image": {
            "url": "https://cdn.discordapp.com/attachments/1292830054715228241/1329103986149560457/IMG_0611.gif?ex=67f7de0b&is=67f68c8b&hm=ba42bda3a5e819bee949231c111c7ee2028a9fb59510877f192fd5dce962a065&"
        }
    }
    
    json_data = {
        "embeds": [embed],
        "content": None  # Remove the plain text content
    }
    
    response = requests.patch(url, headers=headers, json=json_data)
    return response.status_code

@app.route("/webhook", methods=["POST"])
def receive_ping():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return {"error": "Missing user_id"}, 400

    # Update the user's heartbeat timestamp
    user_heartbeats[user_id] = time.time()

    # Update Discord message with the current online count
    update_discord_message()

    return {"message": f"Heartbeat received from {user_id}", "online": len(user_heartbeats)}, 200

def cleanup_thread():
    while True:
        time.sleep(30)  # check every 30 seconds
        now = time.time()
        removed = []

        # Remove users who haven't pinged in the last TIMEOUT_SECONDS
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
    count = len(user_heartbeats)
    return f"""
    <html>
        <head><title>Proxy Status</title></head>
        <body style='font-family:sans-serif; text-align:center; margin-top:100px;'>
            <h1>Online Users</h1>
            <h2 style='font-size:48px'>{count}</h2>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
