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

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# إنشاء مجلد التنزيل
os.makedirs("downloads", exist_ok=True)


# رسالة الترحيب عند /start
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

أنا بوت لتحميل الفيديوهات من:
• يوتيوب
• تيك توك
• إنستغرام
• فيسبوك
• والعديد من المواقع الأخرى

فقط أرسل أي رابط فيديو وسأقوم بتحميله وإرساله لك مباشرة 📥"""
    )


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # تجاهل الرسائل غير النصية
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

    # اسم فريد لكل فيديو حتى لا يعيد الفيديو السابق
    unique_id = str(uuid.uuid4())

    options = {
        "outtmpl": f"downloads/{unique_id}.%(ext)s",
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "cookiefile": "cookies.txt",
        "nocheckcertificate": True,
        "merge_output_format": "mp4",
    }

    try:
        # تحميل الفيديو
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # أحيانًا yt-dlp يغيّر الامتداد بعد الدمج
        if not os.path.exists(file_path):
            base = os.path.splitext(file_path)[0]

            for ext in [".mp4", ".mkv", ".webm"]:
                possible = base + ext
                if os.path.exists(possible):
                    file_path = possible
                    break

        # التحقق من وجود الملف
        if not os.path.exists(file_path):
            await status.edit_text("❌ لم أستطع العثور على الملف بعد التحميل.")
            return

        await status.edit_text("📤 جاري إرسال الفيديو...")
        # إرسال الفيديو كملف لتجنب مشاكل الحجم والمهلة
        with open(file_path, "rb") as video:
                await update.message.reply_document(
        document=video,
        filename=os.path.basename(file_path),
        read_timeout=600,
        write_timeout=600,
        connect_timeout=120,
        pool_timeout=120,
    )

        # حذف رسالة الانتظار
        await status.delete()

        # حذف الملف بعد الإرسال
        os.remove(file_path)

    except Exception as e:
        try:
            await status.edit_text(f"❌ حدث خطأ:\n{str(e)}")
        except:
            await update.message.reply_text(f"❌ حدث خطأ:\n{str(e)}")


# إعداد البوت مع زيادة المهلات
app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .connect_timeout(120)
    .read_timeout(600)
    .write_timeout(600)
    .pool_timeout(120)
    .build()
)

# أمر start
app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, download_video)
)

print("✅ البوت يعمل الآن...")
app.run_polling()
