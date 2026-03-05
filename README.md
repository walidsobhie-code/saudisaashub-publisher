# SaudiSaaSHub Publisher

Automated social media posting bot for SaudiSaaSHub.

## How It Works

1. Every 6 hours, GitHub Actions wakes up
2. Reads RSS feed from https://saudisaashub.pages.dev/feed.xml
3. Checks for new articles
4. Generates posts for Twitter, LinkedIn, Instagram
5. Sends to your Telegram bot

## Setup

1. Go to repo Settings → Secrets and variables → Actions
2. Add these secrets:
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
   - `TELEGRAM_CHAT_ID` - Your chat ID

## Manual Run

Go to Actions → Auto-Post to Social Media → Run workflow

## Files

- `main.py` - Main Python script
- `.github/workflows/auto-post.yml` - GitHub Actions workflow
- `processed_articles.json` - Tracks posted articles

## Notes

- Uses RSS feed for article detection
- Generates 3 post formats (Twitter, LinkedIn, Instagram)
- Runs every 6 hours automatically
