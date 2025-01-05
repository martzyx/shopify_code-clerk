from dotenv import load_dotenv
import os
import json
import pyotp
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import datetime

# Load environment variables
load_dotenv()

# Load Slack tokens and secret key from environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")

# Validate environment variables
if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN or not SECRET_KEY:
    raise ValueError("Missing environment variables. Ensure SLACK_BOT_TOKEN, SLACK_APP_TOKEN, and SECRET_KEY are set.")

# Initialize TOTP
TOTP = pyotp.TOTP(SECRET_KEY)

# Initialize the Slack app
app = App(token=SLACK_BOT_TOKEN)

# File to store usage count and user data
DATA_FILE = "/app/data/user_usage.json"

# Load user usage data from file
def load_user_data():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print("File not found. Initializing user data to an empty dictionary.")
        return {}
    except Exception as e:
        print(f"Error loading user data: {e}")
        return {}

# Save user usage data to file
def save_user_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving user data: {e}")

# Initialize user data
user_data = load_user_data()

@app.message("!shopify")
def send_2fa(message, say, logger):
    global user_data

    # Extract channel ID and user ID from the message
    channel = message.get("channel")
    user_id = message.get("user")
    user_info = app.client.users_info(user=user_id)
    username = user_info["user"]["name"]

    # Increment the interaction count for the user
    user_data[username] = user_data.get(username, 0) + 1
    save_user_data(user_data)

    print(f"Received message: {message}")

    channel_type = message.get("channel_type")
    if channel_type != "im":
        print("Not a DM. Ignoring message.")
        return

    dm_channel = message.get("channel")
    user_id = message.get("user")
    
    if not dm_channel or not user_id:
        print("Missing channel or user information.")
        return

    code = TOTP.now()
    say(text=f"Your TOTP code is: {code}", channel=dm_channel)
    logger.info(f"{username} has interacted with the bot {user_data[username]} times.")
    print(datetime.datetime.utcnow().strftime("%H:%M:%S") + f" Sent 2FA code to {user_id}")

# Start the app with Socket Mode
if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()