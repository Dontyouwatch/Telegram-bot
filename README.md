# Telegram Profile Picture Fetcher Bot

This bot fetches ALL profile pictures of Telegram users when mentioned with their @username.

## Features
- Responds to /start command with instructions
- Fetches ALL profile pictures when users are mentioned with @username
- Shows the total count of profile pictures
- Sends every available profile picture
- Handles multiple username mentions in a single message
- Error handling for non-existent or private profiles
- Progress tracking with picture numbers
- Completion confirmation message

## Requirements
- Python 3.7+
- python-telegram-bot library

## Setup Instructions

1. Install the required package:
```bash
pip install python-telegram-bot
