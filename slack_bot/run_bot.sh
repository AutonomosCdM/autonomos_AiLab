#!/bin/bash

# Simple script to run the Slack bot

# Activate the virtual environment
source venv/bin/activate

# Run the bot
python app.py

# Keep the script running even if there's an error
echo "Bot stopped. Press Ctrl+C to exit."
read -r
