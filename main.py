from typing import Optional
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

logging.basicConfig(level=logging.DEBUG)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']

SLACK_MAIN_CHANNEL = "C06BW33BL8H"

# Install the Slack app and get xoxb- token in advance
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)


@app.event("message")
def handle_message(event, say, context):
    text = event["text"]
    source_channel = event["channel"]
    if "metadata" in event and source_channel == SLACK_MAIN_CHANNEL:
        target_channel = event["metadata"]["event_payload"]["channel_name"]
        print(f"Received message '{text}' from user in channel {source_channel}")
        app.client.chat_postMessage(channel=target_channel, text=text)
        print("message sent...")
    else:
        print("skipped...")


# Event listener for member_joined_channel event
@app.event("member_joined_channel")
def handle_member_joined_channel(event, say):
    user_id = event["user"]
    channel_id = event["channel"]
    # Get user information
    user_info = app.client.users_info(user=user_id)
    user_name = user_info["user"]["real_name"]
    if channel_id == SLACK_MAIN_CHANNEL:
        # Send an introduction message to the channel
        introduction_message = f"Welcome {user_name} to the channel! Feel free to introduce yourself."
        say(introduction_message)
    else:
        print("skipped...")


### All Slash Commands ####
@app.command("/myapp")
def say_hi_to_slash_command(ack, say, body):
    # Acknowledge command request
    ack()
    text = body['text']

    if text:
        say(f"{body['text']}")
    else:
        ack(f":wave: Hi there! <@{body['user_id']}>")


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
