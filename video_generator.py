import os
import uuid
import textwrap
import asyncio
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

from course_curriculum import EPISODES

# ─── إعدادات الفيديو ────────────────────────────────────────────
W, H = 1280, 720
FPS = 24
FONT_PATH = "arabic_font.ttf"
OUTPUT_DIR = "videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── ألوان الثيم ─────────────────────────────────────────────────
BG_TOP    = (10, 15, 40)
BG_BOT    = (25, 35, 80)
ACCENT    = (255, 180, 0)
WHITE     = (255, 255, 255)
LIGHT     = (200, 215, 255)
GRAY      = (140, 155, 195)
SUCCESS   = (80, 200, 120)
CARD_BG   = (30, 45, 90, 220)

BLOCK_COLORS = {
    "event":    (230, 120, 20),
    "variable": (30, 120, 220),
    "logic":    (60, 180, 80),
    "action":   (200, 50, 80),
    "view":     (0, 180, 200),
    "project":  (140, 60, 200),
    "overview": (80, 160, 240),
}


# ─── أدوات مساعدة ────────────────────────────────────────────────

def load_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def ar(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def draw_gradient(draw: ImageDraw.ImageDraw, w: int, h: int):
    for y in range(h):
        t = y / h
        r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def draw_centered_text(draw, text, y, font, color=WHITE, max_w=None):
    if max_w is None:
        max_w = W - 80
    text_ar = ar(text)
    bbox = draw.textbbox((0, 0), text_ar, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, y), text_ar, font=font, fill=color)
    return bbox[3] - bbox[1]


def draw_wrapped_text(draw, text, x, y, font, color, max_width, align="right"):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (word + " " + current).strip()
        bbox = draw.textbbox((0, 0), ar(test), font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current.strip())
            current = word
        else:
            current = test
    if current:
        lines.append(current.strip())

    line_h = font.size + 8
    for line in lines:
        line_ar = ar(line)
        bbox = draw.textbbox((0, 0), line_ar, font=font)
        lw = bbox[2] - bbox[0]
        lx = x + max_width - lw if align == "right" else x
        draw.text((lx, y), line_ar, font=font, fill=color)
        y += line_h
    return y


def draw_header(draw, episode_num, title):
    fn_sm = load_font(22)
    draw.rectangle([(0, 0), (W, 56)], fill=(0, 0, 0, 80))
    ep_text = ar(f"الحلقة {episode_num}")
    draw.text((W - 20, 14), ep_text, font=fn_sm, fill=ACCENT, anchor="ra")
    chan_text = ar("Sketchware بالعربي")
    draw.text((20, 14), chan_text, font=fn_sm, fill=GRAY)


def draw_footer(draw):
    fn_sm = load_font(20)
    draw.rectangle([(0, H - 44), (W, H)], fill=(0, 0, 0, 100))
    sub_text = ar("اشترك في القناة ليصلك كل جديد ✔")
    draw.text((W // 2, H - 25), sub_text, font=fn_sm,
              fill=ACCENT, anchor="mm")


def draw_progress_dots(draw, current, total):
    dot_r = 6
    spacing = 22
    total_w = total * spacing
    start_x = (W - total_w) // 2
    y = H - 52
    for i in range(total):
        cx = start_x + i * spacing + dot_r
        color = ACCENT if i == current else GRAY
        draw.ellipse([(cx - dot_r, y - dot_r), (cx + dot_r, y + dot_r)],
                     fill=color)


# ─── مُنشئو الشرائح ──────────────────────────────────────────────

def make_title_slide(slide: dict, episode_num: int, slide_idx: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H)

    # خطوط زخرفية
    draw.rectangle([(0, 0), (8, H)], fill=ACCENT)
    draw.rectangle([(W - 8, 0), (W, H)], fill=ACCENT)

    fn_title = load_font(64)
    fn_sub   = load_font(30)
    fn_ep    = load_font(40)

    # رقم الحلقة
    ep_str = ar(f"الحلقة {episode_num}")
    bbox = draw.textbbox((0, 0), ep_str, font=fn_ep)
    ew = bbox[2] - bbox[0]
    draw.rounded_rectangle(
        [(W//2 - ew//2 - 24, 130), (W//2 + ew//2 + 24, 188)],
        radius=20, fill=ACCENT,
    )
    draw.text((W // 2, 159), ep_str, font=fn_ep, fill=BG_TOP, anchor="mm")

    # عنوان
    title_ar = ar(slide.get("title", ""))
    draw.text((W // 2, 280), title_ar, font=fn_title, fill=WHITE, anchor="mm")

    # خط فاصل
    draw.rectangle([(W//2 - 160, 345), (W//2 + 160, 349)], fill=ACCENT)

    # subtitle
    sub_ar = ar(slide.get("subtitle", ""))
    draw.text((W // 2, 390), sub_ar, font=fn_sub, fill=LIGHT, anchor="mm")

    draw_footer(draw)
    draw_progress_dots(draw, slide_idx, total)
    return img


def make_content_slide(slide: dict, episode_num: int, slide_idx: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H)

    fn_title  = load_font(46)
    fn_bullet = load_font(32)
    fn_icon   = load_font(38)

    draw_header(draw, episode_num, slide.get("title", ""))

    # عنوان الشريحة
    title_ar = ar(slide.get("title", ""))
    draw.text((W // 2, 108), title_ar, font=fn_title, fill=ACCENT, anchor="mm")

    # خط تحت العنوان
    bbox = draw.textbbox((W//2, 108), title_ar, font=fn_title, anchor="mm")
    tw = bbox[2] - bbox[0]
    draw.rectangle([(W//2 - tw//2, 138), (W//2 + tw//2, 142)], fill=ACCENT)

    # النقاط
    points = slide.get("points", [])
    y = 175
    for i, point in enumerate(points):
        # خلفية النقطة
        draw.rounded_rectangle([(60, y - 8), (W - 60, y + 58)],
                                radius=14, fill=(255, 255, 255, 18))

        # رقم النقطة
        num_ar = ar(str(i + 1))
        draw.ellipse([(80, y + 2), (120, y + 42)], fill=ACCENT)
        draw.text((100, y + 22), num_ar, font=fn_icon, fill=BG_TOP, anchor="mm")

        # نص النقطة
        draw_wrapped_text(draw, point, 130, y + 8, fn_bullet, WHITE,
                          max_width=W - 200, align="right")
        y += 80

    draw_footer(draw)
    draw_progress_dots(draw, slide_idx, total)
    return img


def make_mockup_slide(slide: dict, episode_num: int, slide_idx: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H)

    fn_title  = load_font(42)
    fn_block  = load_font(28)
    fn_label  = load_font(26)

    draw_header(draw, episode_num, slide.get("title", ""))

    title_ar = ar(slide.get("title", ""))
    draw.text((W // 2, 105), title_ar, font=fn_title, fill=ACCENT, anchor="mm")
    draw.rectangle([(W//2 - 140, 132), (W//2 + 140, 135)], fill=ACCENT)

    # محاكاة بيئة Sketchware
    panel_x, panel_y = 60, 155
    panel_w, panel_h = W - 120, H - 230

    # خلفية اللوحة
    draw.rounded_rectangle(
        [(panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h)],
        radius=18, fill=(15, 20, 55), outline=ACCENT, width=2,
    )

    # شريط أعلى اللوحة
    bar_h = 38
    draw.rounded_rectangle(
        [(panel_x, panel_y), (panel_x + panel_w, panel_y + bar_h)],
        radius=18, fill=(30, 40, 90),
    )
    label = ar("Sketchware Block Editor")
    draw.text((panel_x + panel_w // 2, panel_y + bar_h // 2),
              label, font=fn_label, fill=LIGHT, anchor="mm")

    # رسم الكتل
    block_color = BLOCK_COLORS.get(slide.get("block_type", "action"), BLOCK_COLORS["action"])
    points = slide.get("points", [])
    bx = panel_x + 30
    by = panel_y + bar_h + 20
    bw = panel_w - 60

    for i, pt in enumerate(points[:4]):
        shade = tuple(max(0, c - i * 20) for c in block_color)
        draw.rounded_rectangle(
            [(bx, by), (bx + bw, by + 46)],
            radius=10, fill=shade,
        )
        # رمز الكتلة
        draw.rounded_rectangle([(bx + 8, by + 10), (bx + 36, by + 36)],
                                radius=6, fill=(255, 255, 255, 60))
        pt_ar = ar(pt)
        draw.text((bx + bw - 14, by + 23), pt_ar, font=fn_block,
                  fill=WHITE, anchor="rm")
        by += 58

    draw_footer(draw)
    draw_progress_dots(draw, slide_idx, total)
    return img


def make_summary_slide(slide: dict, episode_num: int, slide_idx: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H)

    fn_title  = load_font(48)
    fn_item   = load_font(30)

    draw_header(draw, episode_num, "")

    title_ar = ar("✦ ملخص الحلقة ✦")
    draw.text((W // 2, 108), title_ar, font=fn_title, fill=ACCENT, anchor="mm")
    draw.rectangle([(W//2 - 180, 138), (W//2 + 180, 142)], fill=ACCENT)

    points = slide.get("points", [])
    y = 178
    for pt in points:
        draw.rounded_rectangle([(60, y - 6), (W - 60, y + 52)],
                                radius=12, fill=(40, 60, 120, 160))
        draw.text((W - 80, y + 22), ar("✔"), font=fn_item, fill=SUCCESS, anchor="rm")
        draw_wrapped_text(draw, pt, 80, y + 8, fn_item, WHITE,
                          max_width=W - 140, align="right")
        y += 70

    draw_footer(draw)
    draw_progress_dots(draw, slide_idx, total)
    return img


def make_cta_slide(episode_num: int) -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H)

    fn_big  = load_font(62)
    fn_med  = load_font(36)
    fn_sm   = load_font(26)

    # دائرة مركزية
    cx, cy = W // 2, H // 2 - 40
    r = 130
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                 fill=(30, 50, 120), outline=ACCENT, width=4)

    bell_ar = ar("🔔")
    draw.text((cx, cy - 10), bell_ar, font=fn_big, fill=ACCENT, anchor="mm")

    sub_ar = ar("اشترك في القناة الآن")
    draw.text((W // 2, cy + r + 30), sub_ar, font=fn_med, fill=WHITE, anchor="mm")

    notif_ar = ar("فعّل زر الجرس ليصلك كل جديد")
    draw.text((W // 2, cy + r + 80), notif_ar, font=fn_sm, fill=LIGHT, anchor="mm")

    ep_next = ar(f"الحلقة {episode_num + 1} قادمة قريباً...")
    if episode_num < 20:
        draw.text((W // 2, cy + r + 125), ep_next, font=fn_sm,
                  fill=GRAY, anchor="mm")

    draw.rectangle([(0, 0), (8, H)], fill=ACCENT)
    draw.rectangle([(W - 8, 0), (W, H)], fill=ACCENT)
    return img


# ─── الدالة الرئيسية ─────────────────────────────────────────────

def generate_slide_image(slide: dict, episode_num: int, slide_idx: int, total: int) -> Image.Image:
    stype = slide.get("type", "content")
    if stype == "title":
        return make_title_slide(slide, episode_num, slide_idx, total)
    elif stype in ("mockup",):
        return make_mockup_slide(slide, episode_num, slide_idx, total)
    elif stype == "summary":
        return make_summary_slide(slide, episode_num, slide_idx, total)
    else:
        return make_content_slide(slide, episode_num, slide_idx, total)


def generate_episode_video(episode_num: int, progress_callback=None) -> str:
    if episode_num not in EPISODES:
        raise ValueError(f"الحلقة {episode_num} غير موجودة")

    episode = EPISODES[episode_num]
    slides  = episode["slides"]
    tmp_id  = str(uuid.uuid4())[:8]

    # ─── 1. جمع نصوص التعليق ────────────────────────────────────
    if progress_callback:
        progress_callback("🎙️ جاري توليد التعليق الصوتي...")

    all_narrations = [s.get("narration", "") for s in slides]
    all_narrations.append(
        f"شكراً لمشاهدتك الحلقة {episode_num} من كورس Sketchware. "
        "لا تنسَ الاشتراك وتفعيل الجرس ليصلك كل جديد."
    )

    audio_files = []
    for i, narration in enumerate(all_narrations):
        if not narration.strip():
            continue
        audio_path = f"/tmp/audio_{tmp_id}_{i}.mp3"
        try:
            tts = gTTS(text=narration, lang="ar", slow=False)
            tts.save(audio_path)
            audio_files.append((i, audio_path))
        except Exception as e:
            print(f"⚠️ خطأ في TTS للشريحة {i}: {e}")

    if not audio_files:
        raise RuntimeError("فشل توليد الصوت")

    # ─── 2. إنشاء مقاطع الفيديو ─────────────────────────────────
    if progress_callback:
        progress_callback("🎨 جاري إنشاء الشرائح...")

    clips_with_cta = slides + [{"type": "cta", "narration": all_narrations[-1]}]
    total_slides = len(clips_with_cta)
    video_clips = []

    for idx, (slide_data, (audio_idx, audio_path)) in enumerate(
        zip(clips_with_cta, audio_files)
    ):
        try:
            audio_clip = AudioFileClip(audio_path)
            duration   = max(audio_clip.duration + 0.5, 4.0)

            if slide_data.get("type") == "cta":
                pil_img = make_cta_slide(episode_num)
            else:
                pil_img = generate_slide_image(slide_data, episode_num, idx, total_slides)

            img_path = f"/tmp/slide_{tmp_id}_{idx}.png"
            pil_img.save(img_path)

            img_clip = (
                ImageClip(img_path)
                .with_duration(duration)
                .with_audio(audio_clip)
            )
            video_clips.append(img_clip)

        except Exception as e:
            print(f"⚠️ خطأ في الشريحة {idx}: {e}")

    if not video_clips:
        raise RuntimeError("فشل إنشاء مقاطع الفيديو")

    # ─── 3. دمج المقاطع وحفظ الفيديو ────────────────────────────
    if progress_callback:
        progress_callback("🎬 جاري دمج الفيديو النهائي...")

    final_clip   = concatenate_videoclips(video_clips, method="compose")
    output_path  = os.path.join(OUTPUT_DIR, f"episode_{episode_num:02d}.mp4")

    final_clip.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate="1500k",
        audio_bitrate="128k",
        logger=None,
    )
    final_clip.close()

    # ─── 4. تنظيف الملفات المؤقتة ────────────────────────────────
    for _, ap in audio_files:
        try:
            os.remove(ap)
        except Exception:
            pass
    for i in range(len(clips_with_cta)):
        try:
            os.remove(f"/tmp/slide_{tmp_id}_{i}.png")
        except Exception:
            pass

    return output_path


async def generate_episode_video_async(episode_num: int, progress_callback=None) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, generate_episode_video, episode_num, progress_callback
    )
