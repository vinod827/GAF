from typing import Optional
import slack_sdk
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(level=logging.DEBUG)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']

# Install the Slack app and get xoxb- token in advance
app = App(token=SLACK_BOT_TOKEN)


# Listening to events
# When a user joins the workspace, send a message in a predefined channel asking them to introduce themselves
@app.event("team_join")
def ask_for_introduction(event, say):
    welcome_channel_id = "C12345"
    user_id = event["user"]
    text = f"Welcome to the team, <@{user_id}>! 🎉 You can introduce yourself in this channel."
    say(text=text, channel=welcome_channel_id)


@app.command("/myapp")
def say_hi_to_slash_command(ack, say, body):
    # Acknowledge command request
    ack()
    print("Message body--------------------------------------------------------------------", body)
    say(f"{body['text']}")
    # app.client.chat_postMessage()


@app.command("/hello")
def handle_some_command(ack, context):
    ack(f":wave: Hi there! <@{context.user_id}>")

# Add middleware / listeners here


if __name__ == "__main__":
    # export SLACK_APP_TOKEN=xapp-***
    # export SLACK_BOT_TOKEN=xoxb-***
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
