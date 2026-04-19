from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    CommandHandler,
    filters,
)

import yt_dlp
import os
import uuid
import requests

from flask import Flask
from threading import Thread

from channel_posts import post_to_channel
from video_generator import generate_episode_video_async
from course_curriculum import EPISODES

BOT_TOKEN = os.getenv("BOT_TOKEN")

# إنشاء مجلد التنزيل
os.makedirs("downloads", exist_ok=True)

# ------------------ Flask keep alive ------------------

app_web = Flask("")


@app_web.route("/")
def home():
    return "Bot is running!"


def run_web():
    app_web.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# ------------------ Telegram commands ------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.first_name:
        name = user.first_name
    elif user.username:
        name = user.username
    else:
        name = "صديقي"

    await update.message.reply_text(
        f"""مرحباً {name} 👋

أنا بوت متعدد الوظائف:

📥 *تحميل الفيديوهات* — فقط أرسل أي رابط من:
• يوتيوب • تيك توك • إنستغرام • فيسبوك

📺 *كورس Sketchware بالعربي* — 20 حلقة تعليمية:
• /course — قائمة جميع الحلقات
• /episode 1 — توليد فيديو الحلقة الأولى
• /episode 5 — توليد أي حلقة تريدها""",
        parse_mode="Markdown",
    )


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()

    # التأكد أن الرسالة رابط
    if not url.startswith("http"):
        await update.message.reply_text(
            "❌ أرسل رابط فيديو صحيح من يوتيوب أو تيك توك أو إنستغرام أو فيسبوك."
        )
        return

    status = await update.message.reply_text(
        "⏳ جاري تحميل الفيديو، انتظر قليلاً..."
    )

    # إصلاح روابط TikTok المختصرة vt.tiktok.com
    try:
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
            response = requests.get(
                url,
                allow_redirects=True,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                },
                timeout=20,
            )
            url = response.url
    except:
        pass

    unique_id = str(uuid.uuid4())

    options = {
        "outtmpl": f"downloads/{unique_id}.%(ext)s",
        "format": "bestvideo+bestaudio/best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "cookiefile": "cookies.txt",
        "nocheckcertificate": True,
        "merge_output_format": "mp4",
        "followredirect": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.tiktok.com/",
        },
        "extractor_args": {
            "tiktok": {
                "api_hostname": "api16-normal-c-useast1a.tiktokv.com"
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # البحث عن الملف الحقيقي إذا تغير الامتداد
        if not os.path.exists(file_path):
            base = os.path.splitext(file_path)[0]

            for ext in [".mp4", ".mkv", ".webm"]:
                possible = base + ext
                if os.path.exists(possible):
                    file_path = possible
                    break

        if not os.path.exists(file_path):
            await status.edit_text("❌ لم أستطع العثور على الملف بعد التحميل.")
            return

        await status.edit_text("📤 جاري إرسال الفيديو...")

        with open(file_path, "rb") as video:
            await update.message.reply_document(
                document=video,
                filename=os.path.basename(file_path),
                read_timeout=600,
                write_timeout=600,
                connect_timeout=120,
                pool_timeout=120,
            )

        await status.delete()

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:
        error_text = str(e)

        if "Unsupported URL" in error_text:
            error_text = (
                "هذا الرابط غير مدعوم أو أن TikTok أعاد توجيهه بشكل خاطئ.\n"
                "جرّب إرسال رابط الفيديو المباشر أو الرابط المختصر vt.tiktok.com"
            )

        try:
            await status.edit_text(f"❌ حدث خطأ:\n{error_text}")
        except:
            await update.message.reply_text(f"❌ حدث خطأ:\n{error_text}")


# تشغيل Flask حتى يبقى البوت يعمل
keep_alive()


async def course_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["📚 *كورس Sketchware من الصفر — قائمة الحلقات*\n"]
    for num, ep in EPISODES.items():
        lines.append(f"الحلقة {num}: {ep['title']}")
    lines.append("\n💡 اكتب /episode ثم رقم الحلقة لتوليد فيديوها\nمثال: /episode 1")
    await update.message.reply_text("\n".join(lines))


async def episode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "📺 اكتب رقم الحلقة بعد الأمر.\nمثال: /episode 1"
        )
        return

    try:
        ep_num = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح للحلقة. مثال: /حلقة 3")
        return

    if ep_num not in EPISODES:
        await update.message.reply_text(
            f"❌ الحلقة {ep_num} غير موجودة. الكورس يحتوي {len(EPISODES)} حلقات فقط."
        )
        return

    ep = EPISODES[ep_num]
    status = await update.message.reply_text(
        f"🎬 جاري إنشاء الحلقة {ep_num}: {ep['title']}\n"
        "⏳ هذا قد يستغرق 2–5 دقائق حسب طول الحلقة...\n"
        "سأُبلّغك عند اكتمال كل مرحلة ✔"
    )

    last_msg = [None]

    async def progress(msg: str):
        try:
            m = await update.message.reply_text(msg)
            last_msg[0] = m
        except Exception:
            pass

    try:
        video_path = await generate_episode_video_async(ep_num, progress)

        await status.edit_text(
            f"✅ الحلقة {ep_num} جاهزة!\n📤 جاري الإرسال..."
        )

        with open(video_path, "rb") as vf:
            await update.message.reply_video(
                video=vf,
                caption=(
                    f"📺 *الحلقة {ep_num} — {ep['title']}*\n\n"
                    f"📝 {ep['description']}\n\n"
                    f"🔔 اشترك في القناة ليصلك باقي الحلقات!\n"
                    f"📚 اكتب /course لعرض قائمة الحلقات"
                ),
                parse_mode="Markdown",
                read_timeout=900,
                write_timeout=900,
                connect_timeout=120,
                pool_timeout=120,
            )

        await status.delete()

    except Exception as e:
        await status.edit_text(
            f"❌ حدث خطأ أثناء إنشاء الفيديو:\n{str(e)[:300]}\n\n"
            "جرّب مرة أخرى أو تحقق من اتصال الإنترنت."
        )


async def on_startup(application):
    print("📢 جاري إرسال رسائل القناة...")
    await post_to_channel(application.bot)


# إعداد البوت
app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .connect_timeout(120)
    .read_timeout(600)
    .write_timeout(600)
    .pool_timeout(120)
    .post_init(on_startup)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("course", course_list))
app.add_handler(CommandHandler("episode", episode_cmd))
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, download_video)
)

print("✅ البوت يعمل الآن...")
app.run_polling()
