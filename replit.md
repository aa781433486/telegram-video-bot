# Telegram Video Downloader Bot

A Python Telegram bot that downloads videos from YouTube, TikTok, Instagram, Facebook, and other platforms using `yt-dlp`, then sends them directly to the user.

## Architecture

- **Language**: Python 3.12
- **Framework**: python-telegram-bot (v22.7)
- **Video Downloader**: yt-dlp
- **No database** — stateless, files are deleted after sending

## Key Files

- `bot.py` — Main bot logic with message handlers and video download/send flow
- `cookies.txt` — Cookie file for yt-dlp to access age-restricted content
- `requirements.txt` — Python dependencies

## Environment Variables / Secrets

- `BOT_TOKEN` — Telegram Bot API token (set in Replit Secrets)

## Running

The bot runs via the "Start application" workflow:
```
python bot.py
```

## How It Works

1. User sends `/start` — bot greets them in Arabic
2. User sends a video URL — bot downloads it with yt-dlp and sends it back as a document
3. File is deleted after sending (no persistent storage)

## Notes

- Videos are saved temporarily in the `downloads/` directory (auto-created)
- Extended timeouts (600s read/write) configured for large file transfers
- Supports MP4 format preference with fallback to best available
