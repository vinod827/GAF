from fastapi import FastAPI, Form, HTTPException, Request
from typing import Optional
import slack_sdk
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from slack_sdk.errors import SlackApiError
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.DEBUG)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
SLACK_BOT_USER_OAUTH_TOKEN = os.environ['SLACK_BOT_USER_OAUTH_TOKEN']

client = slack_sdk.WebClient(SLACK_BOT_USER_OAUTH_TOKEN)
app = FastAPI()


@app.post("/")
async def read_root(
        token: Optional[str] = Form(...),
        user_id: Optional[str] = Form(...),
        user_name: Optional[str] = Form(...),
) -> dict:
    # Verify the Slack token
    if token != SLACK_VERIFICATION_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Slack token")
    try:
        print('user_id:', user_id, 'user_name:', user_name)
        # Use the WebClient to send a message with approve and deny buttons
        message = {
            "channel": "#test",
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Approval Request"},
                },
                {
                    "type": "actions",
                    "block_id": "approval_request",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Approve"},
                            "action_id": "approve_button",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Deny"},
                            "action_id": "deny_button",
                        },
                    ],
                },
            ],
        }

        response = client.chat_postMessage(**message)

        # Check the API response for success
        if not response["ok"]:
            raise HTTPException(status_code=500, detail=f"Slack API error: {response['error']}")

        # Process the slash command and generate a response
        response_text = f"Approval request sent to {user_name}."
        print(response_text)
        # Send the response back to Slack
        return {
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
        }

    except SlackApiError as e:
        print(f"Slack API error: {e.response}")
        raise HTTPException(status_code=500, detail="Slack API error")


@app.post("/interactive-endpoint")
async def interactive_endpoint(request: Request):
    try:
        # Log the raw content of the request body
        raw_content = await request.body()
        print(f"Raw Content: {raw_content.decode()}")

        payload = await request.json()
        token = payload.get("token", "")

        # Verify the Slack token
        if token != SLACK_VERIFICATION_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid Slack token")

        callback_id = payload.get("callback_id", "")

        if callback_id == "approval_request":
            # Handle approval request actions
            actions = payload.get("actions", [])
            for action in actions:
                if action.get("action_id") == "approve_button":
                    # Handle approve action
                    user_id = payload.get("user", {}).get("id")
                    # Trigger your backend action for approval

                elif action.get("action_id") == "deny_button":
                    # Handle deny action
                    user_id = payload.get("user", {}).get("id")
                    # Trigger your backend action for denial

        return JSONResponse(content={"message": "Interaction handled"}, status_code=200)

    except Exception as e:
        print(f"Error handling interaction: {e}")
        raise HTTPException(status_code=500, detail="Error handling interaction")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
