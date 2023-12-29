#!/bin/bash

# Set your Slack incoming webhook URL
WEBHOOK_URL="https://hooks.slack.com/services/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"

CHANNEL_NAME="#slave2_public"

# Define your message text and metadata
MESSAGE_TEXT="Message for Slack channel: $CHANNEL_NAME"

# Create the cURL command with the payload
curl -X POST -H 'Content-type: application/json' --data "{
  \"text\": \"$MESSAGE_TEXT\",
  \"metadata\": {
  \"event_type\": \"unified_channel_notification\",
  \"event_payload\": {
      \"channel_name\": \"$CHANNEL_NAME\",
    }
  }
}" $WEBHOOK_URL
