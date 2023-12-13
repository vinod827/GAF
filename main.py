from fastapi import FastAPI, Form, HTTPException
from typing import Optional
import slack_sdk
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

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

    print('user_id:', user_id, 'user_name:', user_name)
    client.chat_postMessage(channel=user_id, text='hello')

    result = client.users_info(
        user=user_id
    )

    # Extract email address from the result
    email = result["user"]["profile"]["email"]

    # Process the slash command and generate a response
    response_text = f"Hello, {user_name}. Your email address is {email}"

    #result = client.users_list()
    #users = result["members"]

    #print(users)
    # Process the slash command and generate a response
    #user_list_text = "\n".join([f"{user['first_name']} ({user['id']})" for user in users])
    #response_text = f"List of all users:\n{user_list_text}"

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
