from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from permissions_manager import AVAILABLE_TOOLS, get_all_permissions, get_all_users


def get_admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🎬 Veo 3 AI — توليد فيديو بالذكاء الاصطناعي", callback_data="admin_veo3")],
        [InlineKeyboardButton("🖼️ تحسين جودة الصور", callback_data="admin_upscale")],
        [InlineKeyboardButton("📖 قصص الأنبياء الكرتونية", callback_data="admin_prophets")],
        [InlineKeyboardButton("📚 كورسات Sketchware", callback_data="admin_course")],
        [InlineKeyboardButton("👥 منح صلاحيات للمستخدمين", callback_data="admin_grant")],
        [InlineKeyboardButton("🚫 إزالة صلاحيات مستخدم", callback_data="admin_revoke")],
        [InlineKeyboardButton("📢 نشر رسائل القناة", callback_data="admin_post_channels")],
        [InlineKeyboardButton("📊 إحصائيات المستخدمين", callback_data="admin_stats")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_tool_selection_keyboard(selected: list) -> InlineKeyboardMarkup:
    rows = []
    for key, label in AVAILABLE_TOOLS.items():
        mark = "✅" if key in selected else "🔲"
        rows.append([InlineKeyboardButton(f"{mark} {label}", callback_data=f"toggle_{key}")])
    rows.append([InlineKeyboardButton("💾 حفظ الصلاحيات", callback_data="confirm_grant")])
    rows.append([InlineKeyboardButton("❌ إلغاء", callback_data="cancel_grant")])
    return InlineKeyboardMarkup(keyboard=rows)


def get_prophet_keyboard() -> InlineKeyboardMarkup:
    from prophet_stories import PROPHETS
    rows = []
    items = list(PROPHETS.items())
    for i in range(0, len(items), 2):
        row = []
        num1, p1 = items[i]
        row.append(InlineKeyboardButton(f"{num1}. {p1['name']}", callback_data=f"prophet_{num1}"))
        if i + 1 < len(items):
            num2, p2 = items[i + 1]
            row.append(InlineKeyboardButton(f"{num2}. {p2['name']}", callback_data=f"prophet_{num2}"))
        rows.append(row)
    rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")])
    return InlineKeyboardMarkup(rows)


def get_veo3_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("✍️ نص ← فيديو", callback_data="veo3_text")],
        [InlineKeyboardButton("🖼️ صورة ← فيديو", callback_data="veo3_image")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_user_tools_keyboard(tools: list) -> InlineKeyboardMarkup:
    keyboard = []
    tool_map = {
        "veo3": ("🎬 Veo 3 AI", "user_veo3"),
        "image_upscaler": ("🖼️ تحسين الصور", "user_upscale"),
        "prophet_stories": ("📖 قصص الأنبياء", "user_prophets"),
    }
    for tool in tools:
        if tool in tool_map:
            label, cb = tool_map[tool]
            keyboard.append([InlineKeyboardButton(label, callback_data=cb)])
    return InlineKeyboardMarkup(keyboard)


def get_post_channels_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📢 نشر في قناة أحمد نجيب", callback_data="post_ahmad")],
        [InlineKeyboardButton("😂 نشر في قناة العوادي 10", callback_data="post_alawodi")],
        [InlineKeyboardButton("📢 نشر في القناتين معاً", callback_data="post_both")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")],
    ]
    return InlineKeyboardMarkup(keyboard)


def format_stats() -> str:
    users = get_all_users()
    perms = get_all_permissions()
    lines = [f"📊 *إحصائيات البوت*\n"]
    lines.append(f"👤 إجمالي المستخدمين: *{len(users)}*")
    lines.append(f"🔑 مستخدمون لهم صلاحيات: *{len(perms)}*\n")
    if perms:
        lines.append("*المستخدمون الممنوحون:*")
        for uname, tools in perms.items():
            tool_names = [AVAILABLE_TOOLS.get(t, t) for t in tools]
            lines.append(f"• @{uname}: {', '.join(tool_names)}")
    return "\n".join(lines)
