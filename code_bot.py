from dotenv import load_dotenv
import os
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

@app.message("!shopify")
def send_2fa(message, say):
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
    print(datetime.datetime.utcnow().strftime("%H:%M:%S") + f" Sent 2FA code to {user_id}")

# Start the app with Socket Mode
if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()