from typing import Optional
import slack_sdk
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_bolt.request import BoltRequest

logging.basicConfig(level=logging.DEBUG)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']

# Install the Slack app and get xoxb- token in advance
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)


# Listening to events
# When a user joins the workspace, send a message in a predefined channel asking them to introduce themselves
# @app.event("team_join")
# def ask_for_introduction(event, say):
#     welcome_channel_id = "C06BW33BL8H"
#     user_id = event["user"]
#     text = f"Welcome to the team, <@{user_id}>! 🎉 You can introduce yourself in this channel."
#     say(text=text, channel=welcome_channel_id)

@app.message()
def handle_message(payload, say, logger, context):
    print(payload)

    event = payload.get('event', {})
    user_id = event.get('user')
    bot_id = context.get('botId')
    text = event.get('text')

    logger.debug(payload)
    say(text)
#
# @app.event("message")
# def handle_message(event, say, context):
#     # user = event["user"]
#     request: BoltRequest = context.request
#
#     # Access custom headers
#     channel_name_header = request.headers.get("Channel_Name")
#     print("Channel Name Header:", channel_name_header)
#
#     print('event:::::::::::::::::::', event)
#     print('context............', context)
#     text = event["text"]
#     channel = event["channel"]
#     target_channel = '#slave2_public'
#
#     # Access query parameters
#     # query_params = context.request.query
#     # print("Query Parameters:", query_params)
#
#     # print("event->>", event["headers"])
#     # Access channel name from the payload
#     # channel_name = event.get("channel_name")
#     # headers = event.get("headers", {})  # Access headers from the event data
#     # print("headers:::", headers)
#     # channel_name = headers.get("Channel_Name")
#     # print("Channel Name:", channel_name)
#
#     print("************************")
#     # Check if the message is from the desired channel
#     if channel == "C06BW33BL8H":  # Replace with your actual channel ID
#         # Do something with the received message
#         print(f"Received message '{text}' from user in channel {channel}")
#         app.client.chat_postMessage(channel=target_channel, text='hello')
#         print("message sent")


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
