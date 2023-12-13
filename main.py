from fastapi import FastAPI, Form, HTTPException
from typing import Optional
import slack_sdk
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

from slack_sdk.errors import SlackApiError

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
        client.chat_postMessage(channel="@nairv", text='hello Slack')

        result = client.users_info(
            user=user_id
        )

        # Extract email address from the result
        email = result["user"]["profile"]["email"]

        # Process the slash command and generate a response
        response_text = f"Hello, {user_name}. Your email address is {email}"

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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
