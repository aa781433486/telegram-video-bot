import os
import uuid
import asyncio
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

FONT_PATH = "arabic_font.ttf"
OUTPUT_DIR = "prophet_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1280, 720
FPS = 24

BG_TOP = (15, 30, 60)
BG_BOT = (40, 15, 60)
GOLD = (212, 175, 55)
WHITE = (255, 255, 255)
LIGHT = (230, 220, 255)


PROPHETS = {
    1: {
        "name": "آدم عليه السلام",
        "title": "قصة أبي البشر آدم",
        "story": [
            "خلق الله آدم عليه السلام من طين، ونفخ فيه من روحه، فصار أول إنسان على وجه الأرض.",
            "أمر الله الملائكة بالسجود لآدم تكريماً له، فسجدوا جميعاً إلا إبليس الذي أبى واستكبر وكفر.",
            "أسكن الله آدم وزوجته حواء الجنة، وأمرهما ألا يقتربا من شجرة بعينها.",
            "وسوس إبليس لهما حتى أكلا من الشجرة، فنزلا إلى الأرض ليبدأ الاختبار الحقيقي للإنسان.",
            "تاب آدم وحواء إلى الله فتاب عليهما، وعلّم الله آدم الأسماء كلها وجعله خليفة في الأرض.",
            "من آدم انتشر البشر على وجه الأرض، وتعلموا الزراعة والبناء وعمارة الأرض بما علمهم الله.",
        ],
    },
    2: {
        "name": "إدريس عليه السلام",
        "title": "قصة النبي إدريس — أول من خط بالقلم",
        "story": [
            "إدريس عليه السلام نبي كريم ذكره الله في القرآن الكريم بالصدق والنبوة والمكانة الرفيعة.",
            "كان أول من خط بالقلم، وأول من خاط الثياب ولبس المخيط، فعلّم الناس الكتابة والخياطة.",
            "درس النجوم والفلك وعلوم الحساب، وكان عالماً حكيماً يدعو قومه إلى عبادة الله وحده.",
            "رفعه الله مكاناً علياً، وأثنى عليه في القرآن قائلاً: وَرَفَعْنَاهُ مَكَانًا عَلِيًّا.",
            "قصة إدريس تعلمنا قيمة العلم والكتابة وأن الله يرفع أهل الصدق والعلم والعمل الصالح.",
        ],
    },
    3: {
        "name": "نوح عليه السلام",
        "title": "قصة نبي الله نوح والطوفان العظيم",
        "story": [
            "بعث الله نوحاً إلى قومه وهم يعبدون الأصنام، فدعاهم ألف سنة إلا خمسين عاماً بالليل والنهار.",
            "لكن قومه أصروا على كفرهم وقالوا: لا تذرن آلهتكم. فآمن معه القليل فقط من قومه.",
            "أوحى الله إلى نوح أن يبني السفينة، فبنى سفينة عظيمة وكان قومه يسخرون منه وهو يبنيها.",
            "أمر الله نوحاً أن يحمل من كل زوجين اثنين، ومن آمن معه، وأهله إلا من سبق عليه القول.",
            "جاء الطوفان العظيم وغرق الكافرون جميعاً حتى ابن نوح الذي أبى ركوب السفينة.",
            "استقرت السفينة على جبل الجودي وانحسر الماء، وبارك الله على نوح والمؤمنين معه وبدأت حياة جديدة.",
        ],
    },
    4: {
        "name": "هود عليه السلام",
        "title": "قصة النبي هود وقوم عاد",
        "story": [
            "بعث الله هوداً إلى قوم عاد، وكانوا أشداء أقوياء يبنون على كل ريع آية ويتخذون المصانع.",
            "دعاهم هود إلى عبادة الله وحده وترك الأصنام، لكنهم استكبروا وقالوا: من أشد منا قوة؟",
            "حذرهم من عذاب الله وقال: إني أخاف عليكم عذاب يوم عظيم. لكنهم لم يتوبوا.",
            "أرسل الله عليهم ريحاً صرصراً عاتية سخرها عليهم سبع ليالٍ وثمانية أيام حسوماً.",
            "دمرت الريح كل شيء وأهلكت قوم عاد، وأنجى الله هوداً والمؤمنين معه برحمة منه.",
            "قصة عاد تذكرنا بأن القوة المادية لا تنفع أمام عذاب الله، والكبر يهلك أصحابه.",
        ],
    },
    5: {
        "name": "صالح عليه السلام",
        "title": "قصة النبي صالح وناقة الله",
        "story": [
            "بعث الله صالحاً إلى قوم ثمود الذين نحتوا الجبال بيوتاً وكانوا في نعمة عظيمة.",
            "طلب قوم ثمود من صالح آية، فأخرج الله لهم ناقة عظيمة من صخرة صماء معجزة باهرة.",
            "قال لهم صالح: هذه ناقة الله لها حق في الشرب ولا تمسوها بسوء فيأخذكم عذاب أليم.",
            "تحدّى الأشقياء الأمر الإلهي، فعقروا الناقة وقالوا: ائت بما تعدنا إن كنت من المرسلين.",
            "أعطاهم صالح مهلة ثلاثة أيام ثم جاءهم الصيحة فأهلكتهم عن آخرهم.",
            "أنجى الله صالحاً والمؤمنين معه. قصة ثمود تعلمنا أن نعمة الله أمانة ولا يُستهان بحدوده.",
        ],
    },
    6: {
        "name": "إبراهيم عليه السلام",
        "title": "قصة خليل الله إبراهيم — أبو الأنبياء",
        "story": [
            "إبراهيم خليل الله، نشأ في بيئة تعبد الأصنام، لكن عقله الفطري رفض الباطل ووصل إلى الحق.",
            "حطّم إبراهيم أصنام قومه بالفأس وترك الكبير فقط، فلما سألوه قال: بل فعله كبيرهم هذا.",
            "ألقوه في النار عقاباً، فجعل الله النار برداً وسلاماً عليه. كانت النار كاليوم الربيعي.",
            "هاجر إلى الأرض المقدسة، ثم إلى مكة حيث ترك ابنه إسماعيل وأمه هاجر في واد غير ذي زرع.",
            "أُمر بذبح ابنه إسماعيل، فامتثل خليل الرحمن وامتثل الابن، ففداه الله بذبح عظيم.",
            "بنى إبراهيم وإسماعيل الكعبة المشرفة، ودعا: ربنا تقبل منا إنك أنت السميع العليم.",
        ],
    },
    7: {
        "name": "يوسف عليه السلام",
        "title": "قصة سيدنا يوسف — أحسن القصص",
        "story": [
            "يوسف بن يعقوب رأى في منامه أحد عشر كوكباً والشمس والقمر يسجدون له، فأخبر أباه.",
            "حسده إخوته فألقوه في البئر وأخبروا أباه بأن الذئب أكله، وجاؤوا على قميصه بدم كذب.",
            "اشتراه تجار من مصر فصار في بيت العزيز، وراودته زوجة العزيز عن نفسه فاستعصم.",
            "سُجن ظلماً لسنوات، لكنه ظل صابراً يعبر الرؤى في السجن، حتى رأى الملك رؤيا عجيبة.",
            "عبّر يوسف الرؤيا بسبع سنوات مخصبة ثم سبع شداد، فجعله الملك على خزائن الأرض.",
            "جاء إخوته يبتغون الطعام فعرفهم ولم يعرفوه، وفي النهاية جمعه الله بأبيه وإخوته وتحققت رؤياه.",
        ],
    },
    8: {
        "name": "موسى عليه السلام",
        "title": "قصة كليم الله موسى وفرعون",
        "story": [
            "ولد موسى في زمن كان فرعون يقتل أبناء بني إسرائيل، فألقت أمه بالوحي موسى في اليمّ.",
            "أنقذه آل فرعون وربوه في قصره، وهكذا أنجز الله خطته المحكمة التي لا يفطن لها أحد.",
            "لما كبر وقتل مصرياً خطأ فرّ إلى مدين حيث عمل لشعيب ثماني سنوات وتزوج ابنته.",
            "كلّمه الله عند الطور من الشجرة: يا موسى إني أنا الله رب العالمين، واختاره نبياً ورسولاً.",
            "أرسله الله إلى فرعون بالمعجزات: العصا واليد البيضاء، وتنين يبتلع السحر والسحرة.",
            "لما أصرّ فرعون أرسل الله عليه الآيات التسع ثم فلق البحر لموسى وأغرق فرعون وجنوده.",
        ],
    },
    9: {
        "name": "سليمان عليه السلام",
        "title": "قصة نبي الله سليمان — ملك الأنبياء",
        "story": [
            "آتى الله سليمان ملكاً عظيماً لم يؤتَه أحد من قبله ولا من بعده: منطق الطير وتسخير الجن والريح.",
            "كانت الجن تعمل له في البناء والحرث والغوص، وجند الله له الريح تجري بأمره رخاء.",
            "تعلم منطق الطير وفهم ما يقوله كل طائر، وكانت جنوده من الإنس والجن والطير.",
            "أرسل الهدهد برسالة إلى ملكة سبأ بلقيس، فأرسلت هدية فردّها سليمان وأتى بعرشها في طرفة عين.",
            "دخلت بلقيس مسلمة لله رب العالمين بعد أن رأت ملك سليمان وحكمته وقصره الزجاجي.",
            "قصة سليمان تعلمنا أن أعظم نعمة هي الشكر، وأن القوة الحقيقية في العدل والتواضع لله.",
        ],
    },
    10: {
        "name": "يونس عليه السلام",
        "title": "قصة النبي يونس — صاحب الحوت",
        "story": [
            "أُرسل يونس إلى أهل نينوى ليدعوهم إلى الله، لكنه غضب منهم وانطلق قبل أن يأذن له ربه.",
            "ركب السفينة في البحر فاضطربت بهم الأمواج، فاقترعوا على من يلقونه فوقعت القرعة على يونس.",
            "ألقوه في البحر فالتقمه الحوت بأمر الله، وصار في ظلمات ثلاث: ظلمة الحوت والبحر والليل.",
            "نادى في الظلمات: لا إله إلا أنت سبحانك إني كنت من الظالمين. فاستجاب الله له.",
            "قذفه الحوت إلى الساحل، وأنبت الله عليه شجرة من يقطين لتظله وهو يستعيد عافيته.",
            "أُرسل ثانية إلى نينوى فتاب قومه جميعاً وآمنوا، وكانت معجزة تذكر الله بها في كتابه.",
        ],
    },
    11: {
        "name": "عيسى عليه السلام",
        "title": "قصة روح الله عيسى المسيح",
        "story": [
            "ولد عيسى من أمه مريم العذراء بأمر الله من غير أب، وكان معجزة باهرة تؤكد قدرة الله.",
            "تكلّم في المهد دفاعاً عن أمه حين قالوا: يا مريم لقد جئتِ شيئاً فرياً. فقال: إني عبد الله.",
            "أيّده الله بروح القدس وآتاه الإنجيل وعلّمه الكتاب والحكمة والتوراة والإنجيل.",
            "أحيا الموتى بإذن الله، وأبرأ الأكمه والأبرص، وخلق من الطين هيئة الطير فنفخ فيها فصارت طيراً.",
            "رفعه الله إليه حين دبّر المشركون إيذاءه، وما صلبوه وما قتلوه ولكن شُبّه لهم.",
            "قصة عيسى تعلمنا أن الله يرفع أولياءه ويحفظهم، وأن الحق يعلو مهما حاول الباطل طمسه.",
        ],
    },
    12: {
        "name": "محمد ﷺ",
        "title": "قصة خاتم الأنبياء والمرسلين محمد ﷺ",
        "story": [
            "وُلد النبي محمد ﷺ في مكة المكرمة عام الفيل، يتيم الأب قبل ولادته والأم في صغره.",
            "رباه جده عبد المطلب ثم عمه أبو طالب، واشتُهر بالأمانة والصدق حتى لقّبه قومه بالأمين.",
            "في الأربعين من عمره نزل عليه جبريل في غار حراء يقول: اقرأ. فكانت أولى آيات القرآن الكريم.",
            "دعا إلى الإسلام سراً ثم جهاراً فآذاه قومه، وهاجر إلى المدينة التي صارت منارة الإسلام.",
            "وحّد العرب بالإسلام وأسس دولة العدل والرحمة، وفتح مكة صفحاً وعفواً عمن آذاه.",
            "أكمل رسالته في حجة الوداع ثم توفي ﷺ وقد أتم الله الدين وأكمله ورضي للمسلمين الإسلام.",
        ],
    },
}


def load_font(size: int):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def render_arabic(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def draw_gradient(draw: ImageDraw.Draw, w: int, h: int):
    for y in range(h):
        t = y / h
        r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def draw_text_centered(draw, text, font, y, color, w):
    rendered = render_arabic(text)
    bbox = font.getbbox(rendered)
    text_w = bbox[2] - bbox[0]
    x = (w - text_w) // 2
    draw.text((x, y), rendered, font=font, fill=color)


def make_slide(title: str, content_line: str, slide_num: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H)

    # Decorative border
    draw.rectangle([(20, 20), (W - 20, H - 20)], outline=GOLD, width=2)

    font_title = load_font(52)
    font_body = load_font(38)
    font_small = load_font(28)

    # Prophet name at top
    draw_text_centered(draw, title, font_title, 60, GOLD, W)

    # Divider
    draw.line([(80, 140), (W - 80, 140)], fill=GOLD, width=2)

    # Content text — wrap
    wrapped = textwrap.wrap(content_line, width=36)
    y = 200
    for line in wrapped:
        draw_text_centered(draw, line, font_body, y, LIGHT, W)
        y += 60

    # Slide counter
    counter = f"{slide_num} / {total}"
    draw_text_centered(draw, counter, font_small, H - 70, GOLD, W)

    # Bismillah at bottom
    draw_text_centered(draw, "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", font_small, H - 110, (180, 160, 220), W)

    return img


def make_title_slide(prophet_name: str, story_title: str) -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, W, H)

    draw.rectangle([(20, 20), (W - 20, H - 20)], outline=GOLD, width=3)
    draw.rectangle([(30, 30), (W - 30, H - 30)], outline=(100, 80, 160), width=1)

    font_big = load_font(64)
    font_mid = load_font(46)
    font_small = load_font(30)

    draw_text_centered(draw, "✨ قصص الأنبياء ✨", font_small, 80, GOLD, W)
    draw.line([(80, 140), (W - 80, 140)], fill=GOLD, width=2)
    draw_text_centered(draw, prophet_name, font_big, 200, WHITE, W)
    draw_text_centered(draw, story_title, font_mid, 310, LIGHT, W)
    draw.line([(80, 400), (W - 80, 400)], fill=GOLD, width=1)
    draw_text_centered(draw, "قصة إيمانية كرتونية", font_small, 440, (180, 160, 220), W)

    return img


async def generate_prophet_video_async(prophet_num: int, progress_callback=None) -> str:
    prophet = PROPHETS.get(prophet_num)
    if not prophet:
        raise Exception(f"النبي رقم {prophet_num} غير موجود.")

    uid = str(uuid.uuid4())[:8]
    tmp_dir = f"/tmp/prophet_{uid}"
    os.makedirs(tmp_dir, exist_ok=True)

    clips = []
    story_lines = prophet["story"]
    total_slides = len(story_lines) + 1

    if progress_callback:
        await progress_callback(f"🎨 جاري إنشاء شرائح قصة {prophet['name']}...")

    # Title slide
    title_img = make_title_slide(prophet["name"], prophet["title"])
    title_path = f"{tmp_dir}/slide_0.jpg"
    title_img.save(title_path, quality=95)

    title_audio_path = f"{tmp_dir}/audio_0.mp3"
    tts_title = gTTS(text=prophet["title"], lang="ar", slow=False)
    tts_title.save(title_audio_path)

    await asyncio.sleep(0.1)

    title_audio = AudioFileClip(title_audio_path)
    title_clip = ImageClip(title_path).with_duration(title_audio.duration + 1)
    title_clip = title_clip.with_audio(title_audio)
    clips.append(title_clip)

    # Story slides
    for i, line in enumerate(story_lines, start=1):
        if progress_callback and i % 2 == 0:
            await progress_callback(f"📖 شريحة {i} من {len(story_lines)}...")

        slide_img = make_slide(prophet["name"], line, i, len(story_lines))
        slide_path = f"{tmp_dir}/slide_{i}.jpg"
        slide_img.save(slide_path, quality=95)

        audio_path = f"{tmp_dir}/audio_{i}.mp3"
        tts = gTTS(text=line, lang="ar", slow=False)
        tts.save(audio_path)

        await asyncio.sleep(0.1)

        audio_clip = AudioFileClip(audio_path)
        img_clip = ImageClip(slide_path).with_duration(audio_clip.duration + 1.5)
        img_clip = img_clip.with_audio(audio_clip)
        clips.append(img_clip)

    if progress_callback:
        await progress_callback("🎬 جاري دمج الشرائح في فيديو...")

    final = concatenate_videoclips(clips, method="compose")
    out_path = f"{OUTPUT_DIR}/prophet_{prophet_num}_{uid}.mp4"

    await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: final.write_videofile(
            out_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        ),
    )

    for clip in clips:
        clip.close()
    final.close()

    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return out_path


def get_prophet_list() -> str:
    lines = ["📖 *قصص الأنبياء الكرتونية — اختر نبياً:*\n"]
    for num, data in PROPHETS.items():
        lines.append(f"{num}. {data['name']}")
    lines.append("\n💡 اضغط على رقم النبي لتوليد فيديو قصته")
    return "\n".join(lines)
