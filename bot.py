from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)

import yt_dlp
import os
import uuid
import requests

from flask import Flask
from threading import Thread

from channel_posts import post_to_channel
from aymen_channel import post_to_aymen_channel
from video_generator import generate_episode_video_async
from course_curriculum import EPISODES
from subscription_check import check_subscription, send_subscription_prompt, CHANNELS
from permissions_manager import (
    is_admin, set_admin_id, get_admin_id, get_user_permissions,
    grant_permission, AVAILABLE_TOOLS,
    is_new_user, register_user, get_all_users,
)
from admin_panel import (
    get_admin_keyboard, get_tool_selection_keyboard,
    get_prophet_keyboard, get_veo3_keyboard,
    get_user_tools_keyboard, format_stats,
)
from image_upscaler import upscale_image
from veo3_handler import generate_video_from_text, generate_video_from_image
from prophet_stories import generate_prophet_video_async, PROPHETS

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PASSWORD = "!?_ayman"

os.makedirs("downloads", exist_ok=True)

user_states = {}

# ─── Flask keep alive ────────────────────────────────────────────────────────

app_web = Flask("")


@app_web.route("/")
def home():
    return "Bot is running!"


def run_web():
    app_web.run(host="0.0.0.0", port=5000)


def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()


# ─── State helpers ────────────────────────────────────────────────────────────

def get_state(user_id: int) -> dict:
    return user_states.get(user_id, {"state": "idle", "data": {}})


def set_state(user_id: int, state: str, data: dict = None):
    user_states[user_id] = {"state": state, "data": data or {}}


def clear_state(user_id: int):
    user_states.pop(user_id, None)


# ─── Subscription helper ─────────────────────────────────────────────────────

async def require_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    if is_admin(user_id):
        return True
    subscribed = await check_subscription(context.bot, user_id)
    if not subscribed:
        await send_subscription_prompt(update, context)
    return subscribed


# ─── Welcome message ─────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    first_name = user.first_name or "صديقي"

    if is_new_user(user_id):
        register_user(user_id, username, first_name)
        admin_id = get_admin_id()
        if admin_id:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"🆕 *مستخدم جديد دخل البوت!*\n\n"
                        f"👤 الاسم: {first_name}\n"
                        f"🔖 المعرف: @{username or 'غير موجود'}\n"
                        f"🆔 ID: `{user_id}`"
                    ),
                    parse_mode="Markdown",
                )
            except Exception:
                pass

    if not await require_subscription(update, context):
        return

    permissions = get_user_permissions(username) if username else []
    has_tools = bool(permissions)

    welcome_text = (
        f"أهلاً وسهلاً {first_name}! 🌟\n\n"
        "╔══════════════════════╗\n"
        "║   🤖 بوت متعدد الذكاء  ║\n"
        "╚══════════════════════╝\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📥 *تحميل الفيديوهات*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "أرسل أي رابط وسأحمّله لك فوراً من:\n"
        "▪ يوتيوب — تيك توك\n"
        "▪ إنستغرام — فيسبوك\n"
        "▪ تويتر/X والمزيد\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📚 *كورس Sketchware بالعربي*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "▪ /course — قائمة الحلقات الـ20\n"
        "▪ /episode 1 — توليد فيديو أي حلقة\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📢 *قنواتنا المميزة*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "▪ @Ahmad_Naguib_Al — تعليم وأمن سيبراني\n"
        "▪ @aymen_alawadi_01 — نكت وعبارات وخلفيات AI"
    )

    if has_tools:
        welcome_text += (
            "\n\n━━━━━━━━━━━━━━━━━━━━\n"
            f"🔑 *أدواتك المتاحة*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "استخدم الأزرار أدناه 👇"
        )
        reply_markup = get_user_tools_keyboard(permissions)
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_text, parse_mode="Markdown")


# ─── Admin Panel ──────────────────────────────────────────────────────────────

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🛡️ *لوحة تحكم المشرف*\n\n"
        "مرحباً بك في لوحة التحكم الخاصة.\n"
        "اختر الأداة التي تريد استخدامها 👇"
    )
    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_admin_keyboard())
    else:
        await update.callback_query.edit_message_text(msg, parse_mode="Markdown", reply_markup=get_admin_keyboard())


# ─── Course commands ──────────────────────────────────────────────────────────

async def course_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_subscription(update, context):
        return
    lines = ["📚 *كورس Sketchware من الصفر — قائمة الحلقات*\n"]
    for num, ep in EPISODES.items():
        lines.append(f"الحلقة {num}: {ep['title']}")
    lines.append("\n💡 اكتب /episode ثم رقم الحلقة\nمثال: /episode 1")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def episode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_subscription(update, context):
        return

    if not context.args:
        await update.message.reply_text("📺 اكتب رقم الحلقة بعد الأمر.\nمثال: /episode 1")
        return

    try:
        ep_num = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح. مثال: /episode 3")
        return

    if ep_num not in EPISODES:
        await update.message.reply_text(
            f"❌ الحلقة {ep_num} غير موجودة. الكورس يحتوي {len(EPISODES)} حلقات."
        )
        return

    ep = EPISODES[ep_num]
    status = await update.message.reply_text(
        f"🎬 جاري إنشاء الحلقة {ep_num}: {ep['title']}\n"
        "⏳ هذا قد يستغرق 2–5 دقائق...\n"
        "سأُبلّغك عند اكتمال كل مرحلة ✔"
    )

    async def progress(msg: str):
        try:
            await update.message.reply_text(msg)
        except Exception:
            pass

    try:
        video_path = await generate_episode_video_async(ep_num, progress)
        await status.edit_text(f"✅ الحلقة {ep_num} جاهزة!\n📤 جاري الإرسال...")
        with open(video_path, "rb") as vf:
            await update.message.reply_video(
                video=vf,
                caption=(
                    f"📺 *الحلقة {ep_num} — {ep['title']}*\n\n"
                    f"📝 {ep['description']}\n\n"
                    "🔔 اشترك في القناة ليصلك باقي الحلقات!\n"
                    "📚 اكتب /course لعرض قائمة الحلقات"
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
            f"❌ حدث خطأ أثناء إنشاء الفيديو:\n{str(e)[:300]}\n\nجرّب مرة أخرى."
        )


# ─── Video download ───────────────────────────────────────────────────────────

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text(
            "❌ أرسل رابط فيديو صحيح من يوتيوب أو تيك توك أو إنستغرام أو فيسبوك."
        )
        return

    if not await require_subscription(update, context):
        return

    status = await update.message.reply_text("⏳ جاري تحميل الفيديو، انتظر قليلاً...")

    try:
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
            response = requests.get(
                url, allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=20,
            )
            url = response.url
    except Exception:
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.tiktok.com/",
        },
        "extractor_args": {
            "tiktok": {"api_hostname": "api16-normal-c-useast1a.tiktokv.com"}
        },
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

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
        except Exception:
            pass

    except Exception as e:
        error_text = str(e)
        if "Unsupported URL" in error_text:
            error_text = "هذا الرابط غير مدعوم. جرّب إرسال رابط مباشر."
        try:
            await status.edit_text(f"❌ حدث خطأ:\n{error_text}")
        except Exception:
            await update.message.reply_text(f"❌ حدث خطأ:\n{error_text}")


# ─── Photo handler ────────────────────────────────────────────────────────────

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    user_id = update.effective_user.id
    st = get_state(user_id)

    if not await require_subscription(update, context):
        return

    # Image upscaler
    if st["state"] in ("upscaling", "user_upscaling"):
        status = await update.message.reply_text("🔍 جاري تحسين جودة الصورة...")
        try:
            photo = update.message.photo[-1]
            photo_file = await context.bot.get_file(photo.file_id)
            image_bytes = await photo_file.download_as_bytearray()

            enhanced = upscale_image(bytes(image_bytes))

            import io as _io
            await status.edit_text("📤 جاري إرسال الصورة المحسّنة...")
            await update.message.reply_document(
                document=_io.BytesIO(enhanced),
                filename="enhanced_image.jpg",
                caption=(
                    "✅ *تم تحسين الصورة بنجاح!*\n\n"
                    "🔬 رُفعت الدقة 4× مع تحسين الحدة والألوان\n"
                    "📌 لا تغيير في الملامح أو محتوى الصورة"
                ),
                parse_mode="Markdown",
            )
            await status.delete()
        except Exception as e:
            await status.edit_text(f"❌ خطأ في التحسين: {str(e)[:200]}")
        finally:
            clear_state(user_id)
        return

    # Veo3 image-to-video: got image
    if st["state"] == "veo3_image":
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        image_bytes = bytes(await photo_file.download_as_bytearray())

        set_state(user_id, "veo3_image_prompt", {"image_bytes": image_bytes})
        await update.message.reply_text(
            "🖼️ تم استلام الصورة!\n\n"
            "✍️ الآن أرسل *وصفاً* للحركة أو المشهد الذي تريده في الفيديو:\n"
            "مثال: «أشجار تتحرك في النسيم، إضاءة ذهبية عند غروب الشمس»",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text("ℹ️ أرسل رابطاً لتحميل فيديو، أو استخدم الأزرار للوصول إلى الأدوات.")


# ─── Text message handler ─────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user_id = update.effective_user.id
    username = update.effective_user.username or ""

    # Admin authentication
    if text == ADMIN_PASSWORD:
        set_admin_id(user_id)
        await show_admin_panel(update, context)
        return

    st = get_state(user_id)

    # Waiting for grant username
    if st["state"] == "grant_username":
        target = text.lstrip("@").strip()
        set_state(user_id, "grant_selecting", {"target": target, "selected": []})
        await update.message.reply_text(
            f"👤 المستخدم: @{target}\n\n"
            "اختر الأدوات التي تريد منحها 👇\n"
            "(اضغط على كل أداة لتحديدها أو إلغاء تحديدها)",
            reply_markup=get_tool_selection_keyboard([]),
        )
        return

    # Waiting for Veo3 text prompt
    if st["state"] in ("veo3_text", "user_veo3_text"):
        async def progress(msg):
            try:
                await update.message.reply_text(msg)
            except Exception:
                pass

        status = await update.message.reply_text("🎬 جاري إرسال طلبك إلى Veo 3 AI...")
        clear_state(user_id)
        try:
            video_bytes = await generate_video_from_text(text, progress)
            await status.edit_text("📤 جاري إرسال الفيديو المُولَّد...")
            import io as _io
            await update.message.reply_video(
                video=_io.BytesIO(video_bytes),
                caption=(
                    f"✅ *فيديو Veo 3 AI*\n\n"
                    f"📝 الوصف: {text[:100]}"
                ),
                parse_mode="Markdown",
                read_timeout=600, write_timeout=600,
            )
            await status.delete()
        except Exception as e:
            await status.edit_text(f"❌ خطأ في Veo 3: {str(e)[:300]}")
        return

    # Waiting for Veo3 image prompt (after image was received)
    if st["state"] == "veo3_image_prompt":
        image_bytes = st["data"].get("image_bytes")

        async def progress(msg):
            try:
                await update.message.reply_text(msg)
            except Exception:
                pass

        status = await update.message.reply_text("🎬 جاري تحويل الصورة إلى فيديو بـ Veo 3...")
        clear_state(user_id)
        try:
            video_bytes = await generate_video_from_image(image_bytes, text, progress)
            await status.edit_text("📤 جاري إرسال الفيديو المُولَّد...")
            import io as _io
            await update.message.reply_video(
                video=_io.BytesIO(video_bytes),
                caption="✅ *تم تحويل الصورة إلى فيديو بـ Veo 3 AI!*",
                parse_mode="Markdown",
                read_timeout=600, write_timeout=600,
            )
            await status.delete()
        except Exception as e:
            await status.edit_text(f"❌ خطأ في Veo 3: {str(e)[:300]}")
        return

    # URL download
    if text.startswith("http"):
        await download_video(update, context)
        return

    # Default
    if not await require_subscription(update, context):
        return

    permissions = get_user_permissions(username) if username else []
    if permissions:
        await update.message.reply_text(
            "👇 استخدم الأزرار للوصول إلى أدواتك:",
            reply_markup=get_user_tools_keyboard(permissions),
        )
    else:
        await update.message.reply_text(
            "أرسل رابط فيديو لتحميله، أو استخدم:\n"
            "/start — الرئيسية\n"
            "/course — قائمة الحلقات\n"
            "/episode [رقم] — توليد حلقة"
        )


# ─── Callback queries ─────────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    username = query.from_user.username or ""

    # Subscription check
    if data == "check_subscription":
        subscribed = await check_subscription(context.bot, user_id)
        if subscribed:
            await query.edit_message_text(
                "✅ *تم التحقق من اشتراكك بنجاح!*\n\nاضغط /start لبدء الاستخدام.",
                parse_mode="Markdown",
            )
        else:
            channel_links = " | ".join([f"[{c['name']}]({c['url']})" for c in CHANNELS])
            await query.edit_message_text(
                f"❌ لم تشترك بعد في جميع القنوات.\n\n{channel_links}\n\nبعد الاشتراك اضغط التحقق مجدداً.",
                parse_mode="Markdown",
                reply_markup=query.message.reply_markup,
            )
        return

    # Admin back
    if data == "admin_back":
        if not is_admin(user_id):
            await query.answer("غير مصرح.", show_alert=True)
            return
        await show_admin_panel(update, context)
        return

    # Admin stats
    if data == "admin_stats":
        if not is_admin(user_id):
            await query.answer("غير مصرح.", show_alert=True)
            return
        await query.edit_message_text(
            format_stats(),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]),
        )
        return

    # Admin veo3
    if data == "admin_veo3":
        if not is_admin(user_id):
            await query.answer("غير مصرح.", show_alert=True)
            return
        await query.edit_message_text(
            "🎬 *Veo 3 AI — توليد الفيديو*\n\n"
            "اختر نوع التوليد:",
            parse_mode="Markdown",
            reply_markup=get_veo3_keyboard(),
        )
        return

    # Veo3 text
    if data in ("veo3_text", "user_veo3"):
        if data == "veo3_text" and not is_admin(user_id):
            await query.answer("غير مصرح.", show_alert=True)
            return
        if data == "user_veo3":
            perms = get_user_permissions(username)
            if "veo3" not in perms:
                await query.answer("ليس لديك صلاحية.", show_alert=True)
                return

        state_key = "veo3_text" if data == "veo3_text" else "user_veo3_text"
        set_state(user_id, state_key)
        await query.edit_message_text(
            "🎬 *Veo 3 AI — نص إلى فيديو*\n\n"
            "✍️ أرسل وصفاً تفصيلياً للفيديو الذي تريد توليده:\n\n"
            "💡 *مثال:*\n"
            "«مدينة مستقبلية تحت المطر، أضواء نيون، سيارات طائرة، جو خيالي»",
            parse_mode="Markdown",
        )
        return

    # Veo3 image
    if data == "veo3_image":
        if not is_admin(user_id):
            await query.answer("غير مصرح.", show_alert=True)
            return
        set_state(user_id, "veo3_image")
        await query.edit_message_text(
            "🖼️ *Veo 3 AI — صورة إلى فيديو*\n\n"
            "📸 أرسل الصورة التي تريد تحريكها:",
            parse_mode="Markdown",
        )
        return

    # Admin upscale
    if data in ("admin_upscale", "user_upscale"):
        if data == "admin_upscale" and not is_admin(user_id):
            await query.answer("غير مصرح.", show_alert=True)
            return
        if data == "user_upscale":
            perms = get_user_permissions(username)
            if "image_upscaler" not in perms:
                await query.answer("ليس لديك صلاحية.", show_alert=True)
                return

        state_key = "upscaling" if data == "admin_upscale" else "user_upscaling"
        set_state(user_id, state_key)
        await query.edit_message_text(
            "🖼️ *تحسين جودة الصور*\n\n"
            "📸 أرسل الصورة التي تريد تحسينها:\n\n"
            "✅ سيتم رفع الدقة 4× مع تحسين الحدة\n"
            "🔒 لا تغيير في الملامح أو محتوى الصورة",
            parse_mode="Markdown",
        )
        return

    # Admin prophets / user prophets
    if data in ("admin_prophets", "user_prophets"):
        if data == "admin_prophets" and not is_admin(user_id):
            await query.answer("غير مصرح.", show_alert=True)
            return
        if data == "user_prophets":
            perms = get_user_permissions(username)
            if "prophet_stories" not in perms:
                await query.answer("ليس لديك صلاحية.", show_alert=True)
                return

        await query.edit_message_text(
            "📖 *قصص الأنبياء الكرتونية*\n\nاختر نبياً لتوليد فيديو قصته 👇",
            parse_mode="Markdown",
            reply_markup=get_prophet_keyboard(),
        )
        return

    # Generate prophet video
    if data.startswith("prophet_"):
        try:
            prophet_num = int(data.split("_")[1])
        except (IndexError, ValueError):
            return

        prophet = PROPHETS.get(prophet_num)
        if not prophet:
            await query.answer("النبي غير موجود.", show_alert=True)
            return

        await query.edit_message_text(
            f"🎬 *جاري إنشاء فيديو قصة {prophet['name']}*\n\n"
            "⏳ هذا قد يستغرق 2–5 دقائق...\n"
            "سأُبلّغك عند اكتمال كل مرحلة ✔",
            parse_mode="Markdown",
        )

        async def progress(msg):
            try:
                await context.bot.send_message(chat_id=query.message.chat_id, text=msg)
            except Exception:
                pass

        try:
            video_path = await generate_prophet_video_async(prophet_num, progress)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"✅ فيديو قصة {prophet['name']} جاهز!\n📤 جاري الإرسال...",
            )
            with open(video_path, "rb") as vf:
                await context.bot.send_video(
                    chat_id=query.message.chat_id,
                    video=vf,
                    caption=(
                        f"📖 *قصة {prophet['name']}*\n\n"
                        f"🎬 {prophet['title']}\n\n"
                        "اشترك في قناتينا ليصلك المزيد!"
                    ),
                    parse_mode="Markdown",
                    read_timeout=900, write_timeout=900,
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ حدث خطأ: {str(e)[:300]}",
            )
        return

    # Admin grant
    if data == "admin_grant":
        if not is_admin(user_id):
            await query.answer("غير مصرح.", show_alert=True)
            return
        set_state(user_id, "grant_username")
        await query.edit_message_text(
            "👥 *منح صلاحيات للمستخدمين*\n\n"
            "✍️ أرسل اسم المستخدم الذي تريد منحه صلاحية:\n"
            "مثال: @username",
            parse_mode="Markdown",
        )
        return

    # Toggle tool in permission selection
    if data.startswith("toggle_"):
        if not is_admin(user_id):
            await query.answer("غير مصرح.", show_alert=True)
            return
        st = get_state(user_id)
        if st["state"] != "grant_selecting":
            await query.answer("انتهت الجلسة. ابدأ من جديد.", show_alert=True)
            return

        tool_key = data[len("toggle_"):]
        selected = list(st["data"].get("selected", []))
        if tool_key in selected:
            selected.remove(tool_key)
        else:
            selected.append(tool_key)

        set_state(user_id, "grant_selecting", {**st["data"], "selected": selected})
        target = st["data"].get("target", "")

        tool_labels = [AVAILABLE_TOOLS.get(t, t) for t in selected]
        selected_text = "\n".join(f"• {l}" for l in tool_labels) if tool_labels else "لا شيء محدد"

        await query.edit_message_text(
            f"👤 المستخدم: @{target}\n\n"
            f"*الأدوات المحددة:*\n{selected_text}\n\n"
            "اضغط على الأدوات للتحديد أو الإلغاء:",
            parse_mode="Markdown",
            reply_markup=get_tool_selection_keyboard(selected),
        )
        return

    # Confirm grant
    if data == "confirm_grant":
        if not is_admin(user_id):
            await query.answer("غير مصرح.", show_alert=True)
            return
        st = get_state(user_id)
        if st["state"] != "grant_selecting":
            await query.answer("انتهت الجلسة.", show_alert=True)
            return

        target = st["data"].get("target", "")
        selected = st["data"].get("selected", [])
        clear_state(user_id)

        if not selected:
            await query.edit_message_text(
                "⚠️ لم تختر أي أداة. تم إلغاء العملية.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]),
            )
            return

        grant_permission(target, selected)
        tool_labels = [AVAILABLE_TOOLS.get(t, t) for t in selected]
        selected_text = "\n".join(f"✅ {l}" for l in tool_labels)

        await query.edit_message_text(
            f"✅ *تم منح الصلاحيات بنجاح!*\n\n"
            f"👤 المستخدم: @{target}\n\n"
            f"*الأدوات الممنوحة:*\n{selected_text}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]),
        )
        return

    # Cancel grant
    if data == "cancel_grant":
        clear_state(user_id)
        await show_admin_panel(update, context)
        return


# ─── On startup ───────────────────────────────────────────────────────────────

async def on_startup(application):
    print("📢 جاري إرسال رسائل القناة الأولى...")
    await post_to_channel(application.bot)
    print("📢 جاري إرسال رسائل قناة أيمن...")
    await post_to_aymen_channel(application.bot)


# ─── Bot setup ────────────────────────────────────────────────────────────────

keep_alive()

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
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    import traceback
    err = str(context.error)
    if "Conflict" in err:
        print("⚠️ تعارض في نسخ البوت — جارٍ الحل...")
        return
    print(f"❌ خطأ: {err}")


app.add_error_handler(error_handler)

print("✅ البوت يعمل الآن...")
app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
