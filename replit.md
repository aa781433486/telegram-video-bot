# Telegram Video Downloader Bot + Sketchware Course Generator

A Python Telegram bot with three main features:
1. Downloads videos from YouTube, TikTok, Instagram, Facebook via yt-dlp
2. Auto-posts Arabic cybersecurity messages to a Telegram channel on startup
3. Generates animated slide-based course videos for a Sketchware Android development tutorial

## Architecture

- **Language**: Python 3.12
- **Framework**: python-telegram-bot (v22.7)
- **Video Downloader**: yt-dlp
- **Video Generator**: moviepy + Pillow + gTTS (Arabic TTS)
- **Arabic Text**: arabic-reshaper + python-bidi
- **Font**: Noto Sans Arabic (arabic_font.ttf)

## Key Files

| File | Description |
|------|-------------|
| `bot.py` | Main bot — handlers for /start, /course, /episode, video download |
| `channel_posts.py` | Auto-posts cybersecurity messages to @Ahmad_Naguib_Al on startup |
| `sent_messages.json` | Tracks sent channel posts to avoid repetition |
| `course_curriculum.py` | 20-episode Sketchware course data (titles, slides, narration scripts) |
| `video_generator.py` | Creates 1280x720 MP4 videos: Pillow slides + Arabic TTS + moviepy |
| `arabic_font.ttf` | Noto Sans Arabic font for rendering Arabic text in Pillow |
| `cookies.txt` | yt-dlp cookies for age-restricted content |
| `requirements.txt` | Python dependencies |
| `videos/` | Output directory for generated episode videos |

## Bot Commands

- `/start` — Welcome message with feature overview
- `/course` — Lists all 20 Sketchware course episodes
- `/episode <N>` — Generates and sends episode N as an animated MP4 video (1–20)
- Any URL — Downloads and sends the video from YouTube/TikTok/Instagram/Facebook

## Environment Variables / Secrets

- `BOT_TOKEN` — Telegram Bot API token (set in Replit Secrets)

## Channel

- **Channel ID**: @Ahmad_Naguib_Al
- Bot is admin with posting permission

## Sketchware Course Content (20 Episodes)

1. مقدمة إلى Sketchware
2. تثبيت Sketchware وأول مشروع
3. التصميم — Layout وترتيب العناصر
4. TextView وButton — أول تفاعل
5. EditText وImageView
6. الأحداث (Events)
7. المتغيرات (Variables)
8. الشروط (If-Else)
9. الحلقات (Loops)
10. القوائم (Lists)
11. Intent — التنقل بين الشاشات
12. SharedPreferences
13. SQLite Database
14. الإنترنت — RequestNetwork
15. JSON Parser
16. RecyclerView
17. الإشعارات والكاميرا
18. المؤقت (Timer)
19. الدوال (Functions)
20. مشروع نهائي ونشر على Google Play

## Video Generation Details

- Resolution: 1280 × 720 (16:9)
- FPS: 24
- Bitrate: 1500k video / 128k audio
- Arabic TTS: gTTS lang="ar"
- Slide types: title, content, mockup (Sketchware block simulator), summary, CTA
- Slide duration = audio duration + 0.5s (min 4s)
- Videos saved to `videos/episode_NN.mp4`
