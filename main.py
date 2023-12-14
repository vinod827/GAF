from fastapi import FastAPI, Form, HTTPException, Request, Body
from typing import Optional, Dict, Union, List
import slack_sdk
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from slack_sdk.errors import SlackApiError
from fastapi.responses import JSONResponse
from urllib.parse import unquote
import json

from starlette.responses import JSONResponse

logging.basicConfig(level=logging.DEBUG)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
SLACK_BOT_USER_OAUTH_TOKEN = os.environ['SLACK_BOT_USER_OAUTH_TOKEN']

client = slack_sdk.WebClient(SLACK_BOT_USER_OAUTH_TOKEN)
app = FastAPI()


@app.post("/request-repo-access")
async def read_repo_access_request(
        token: str = Form(...),
        user_id: str = Form(...),
        user_name: str = Form(...),
        project: str = Form("", alias="text"),
        role: str = Form("", alias="text"),
) -> JSONResponse:
    # Verify the Slack token
    if token != SLACK_VERIFICATION_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Slack token")

    # Extract the project name from the command text
    if not project:
        return JSONResponse(content={"text": "Please provide a project name in the Slack command, for instance - "
                                             "/request-repo-access pylon"}, status_code=200)

    try:
        print('user_id:', user_id, 'user_name:', user_name, 'project:', project)
        # Use the WebClient to send a message with approve and deny buttons
        # Set the channel and message text
        channel = "#test"
        message_text = f":memo: Access Request for GitLab project repository *{project}* from *{user_name}*"
        blocks = [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": message_text},
            },
            {
                "type": "actions",
                "block_id": "approval_request",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": ":white_check_mark: Approve"},
                        "action_id": "approve_button",
                        "style": "primary",  # Set the style to "primary" for a green button
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": ":x: Deny"},
                        "action_id": "deny_button",
                        "style": "danger",  # Set the style to "danger" for a red button
                    },
                    {
                        "type": "static_select",
                        "action_id": "approval_duration",
                        "placeholder": {
                            "type": "plain_text",
                            "text": ":calendar: Select duration for Maintainer role",
                        },
                        "options": [
                            {
                                "text": {"type": "plain_text", "text": ":clock1: 15 days"},
                                "value": "15",
                            },
                            {
                                "text": {"type": "plain_text", "text": ":clock3: 30 days"},
                                "value": "30",
                            },
                            {
                                "text": {"type": "plain_text", "text": ":infinity: Always"},
                                "value": "A",
                            },
                        ]
                    }
                ],
            },
        ]

        response = client.chat_postMessage(
            channel=channel,
            text=message_text,
            blocks=blocks
        )

        # Check the API response for success
        if not response["ok"]:
            raise HTTPException(status_code=500, detail=f"Slack API error: {response['error']}")

        # Process the slash command and generate a response
        response_text = f"Approval request sent to {user_name}."
        print(response_text)
        # Send the response back to Slack
        return JSONResponse(content={
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": response_text
                    }
                }
            ]
        })

    except SlackApiError as e:
        print(f"Slack API error: {e.response}")
        raise HTTPException(status_code=500, detail="Slack API error")


@app.post("/interactive-endpoint")
async def interactive_endpoint(payload: str = Body(...)):
    try:
        # URL decode the payload
        decoded_payload = unquote(payload)
        print('decoded_payload:', decoded_payload)
        payload_data = decoded_payload

        contains_equal_sign = '=' in decoded_payload
        if contains_equal_sign:
            # Split the string at the equal sign
            split_result = decoded_payload.split('=')

            # Extract the second part of the split result (after the equal sign)
            payload_data = split_result[1]

            # Add a check for empty payload
            if not payload_data:
                return {"error": "Empty payload"}

        # Parse the payload as JSON
        payload_json = json.loads(payload_data)
        print('payload_json:', payload_json)

        # Log the parsed payload
        token = payload_json.get("token", "")

        # Verify the Slack token
        if token != SLACK_VERIFICATION_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid Slack token")

        actions = payload_json.get("actions", [])
        for action in actions:
            # Check if the action is related to the dropdown
            if action["action_id"] == "approval_duration":
                # Ignore the action for the dropdown and return early
                return JSONResponse(content={"message": "Dropdown value selected"}, status_code=200)

            if action["action_id"] == "approve_button":
                # Handle approve action
                # Trigger your backend action for approval
                print("Request approved")
                return JSONResponse(content={"message": "Approved"}, status_code=200)

            elif action["action_id"] == "deny_button":
                # Handle deny action
                # Return a message with a text box for remarks
                print("Request denied")
                return JSONResponse(
                    content={
                        "message": "Please provide remarks for denying the request",
                        "attachments": [
                            {
                                "text": "Remarks:",
                                "fallback": "You are unable to enter remarks.",
                                "callback_id": "deny_remarks",
                                "color": "#3AA3E3",
                                "attachment_type": "default",
                                "actions": [
                                    {
                                        "name": "remarks",
                                        "text": "Enter Remarks",
                                        "type": "text",
                                        "placeholder": "Enter your remarks here"
                                    }
                                ]
                            }
                        ]
                    },
                    status_code=200
                )

        return JSONResponse(content={"message": "Interaction handled"}, status_code=200)

    except Exception as e:
        print(f"Error handling interaction: {e}")
        raise HTTPException(status_code=500, detail="Error handling interaction")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
