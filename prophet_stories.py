import os
import uuid
import asyncio
import math
import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

FONT_PATH = "arabic_font.ttf"
OUTPUT_DIR = "prophet_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1280, 720
FPS = 24

PROPHETS = {
    1: {
        "name": "آدم عليه السلام",
        "title": "قصة أبي البشر آدم",
        "color_theme": ((20, 80, 40), (10, 50, 20)),
        "scenes": [
            {
                "text": "في البداية خلق الله آدم عليه السلام من طين الأرض، ونفخ فيه من روحه فصار أول إنسان.",
                "setting": "garden",
                "chars": ["adam"],
                "mood": "wonder",
            },
            {
                "text": "أمر الله الملائكة بالسجود لآدم تكريماً له، فسجدوا جميعاً إلا إبليس الذي أبى واستكبر.",
                "setting": "heaven",
                "chars": ["adam", "iblis"],
                "mood": "conflict",
            },
            {
                "text": "أسكن الله آدم وزوجته حواء الجنة في نعيم وسعادة، وأمرهما ألا يقتربا من شجرة بعينها.",
                "setting": "paradise",
                "chars": ["adam", "hawwa"],
                "mood": "happy",
            },
            {
                "text": "وسوس إبليس لهما حتى أكلا من الشجرة، فنزلا إلى الأرض ليبدأ اختبار الإنسان الحقيقي.",
                "setting": "earth",
                "chars": ["adam", "hawwa"],
                "mood": "sad",
            },
            {
                "text": "تاب آدم وحواء إلى الله، فتاب عليهما وعلّمهما وجعل آدم خليفة في الأرض.",
                "setting": "earth",
                "chars": ["adam"],
                "mood": "peaceful",
            },
            {
                "text": "من آدم انتشر البشر في الأرض وتعلموا الزراعة والبناء وعمارة الأرض بما علمهم الله.",
                "setting": "earth",
                "chars": ["family"],
                "mood": "hopeful",
            },
        ],
    },
    2: {
        "name": "إدريس عليه السلام",
        "title": "قصة النبي إدريس — أول من خط بالقلم",
        "color_theme": ((20, 40, 80), (10, 20, 60)),
        "scenes": [
            {
                "text": "إدريس عليه السلام نبي كريم ذكره الله في القرآن بالصدق والنبوة والمكانة الرفيعة.",
                "setting": "school",
                "chars": ["prophet"],
                "mood": "wise",
            },
            {
                "text": "كان أول من خط بالقلم وأول من خاط الثياب، فعلّم الناس فنون الكتابة والخياطة.",
                "setting": "school",
                "chars": ["prophet", "students"],
                "mood": "teaching",
            },
            {
                "text": "درس النجوم والفلك وعلوم الحساب، وكان عالماً حكيماً يدعو قومه إلى الله.",
                "setting": "night_sky",
                "chars": ["prophet"],
                "mood": "wonder",
            },
            {
                "text": "رفعه الله مكاناً علياً وأثنى عليه في القرآن: وَرَفَعْنَاهُ مَكَانًا عَلِيًّا.",
                "setting": "heaven",
                "chars": ["prophet"],
                "mood": "peaceful",
            },
            {
                "text": "قصة إدريس تعلمنا قيمة العلم والكتابة وأن الله يرفع أهل الصدق والعلم والعمل الصالح.",
                "setting": "school",
                "chars": ["students"],
                "mood": "hopeful",
            },
        ],
    },
    3: {
        "name": "نوح عليه السلام",
        "title": "قصة نبي الله نوح والطوفان العظيم",
        "color_theme": ((10, 30, 80), (20, 60, 100)),
        "scenes": [
            {
                "text": "بعث الله نوحاً إلى قومه وهم يعبدون الأصنام، فدعاهم ألف سنة إلا خمسين عاماً.",
                "setting": "village",
                "chars": ["noah", "crowd"],
                "mood": "preaching",
            },
            {
                "text": "قومه أصروا على كفرهم وسخروا من نوح، فآمن معه القليل فقط وهو صابر محتسب.",
                "setting": "village",
                "chars": ["noah", "crowd"],
                "mood": "conflict",
            },
            {
                "text": "أوحى الله إلى نوح أن يبني السفينة العظيمة، وقومه يسخرون منه وهو يبنيها بصبر.",
                "setting": "ark_building",
                "chars": ["noah"],
                "mood": "working",
            },
            {
                "text": "حمل نوح من كل زوجين اثنين ومن آمن معه، وركبوا السفينة بسم الله.",
                "setting": "ark",
                "chars": ["noah", "animals", "believers"],
                "mood": "hopeful",
            },
            {
                "text": "جاء الطوفان العظيم وغرق الكافرون، حتى ابن نوح الذي أبى ركوب السفينة.",
                "setting": "flood",
                "chars": ["ark"],
                "mood": "dramatic",
            },
            {
                "text": "استقرت السفينة على جبل الجودي، وبارك الله على نوح والمؤمنين وبدأت حياة جديدة.",
                "setting": "mountain",
                "chars": ["noah", "believers"],
                "mood": "peaceful",
            },
        ],
    },
    4: {
        "name": "هود عليه السلام",
        "title": "قصة النبي هود وقوم عاد",
        "color_theme": ((80, 50, 10), (60, 30, 5)),
        "scenes": [
            {
                "text": "بعث الله هوداً إلى قوم عاد الأشداء الأقوياء الذين يبنون على كل مكان عالٍ.",
                "setting": "desert",
                "chars": ["hud", "crowd"],
                "mood": "preaching",
            },
            {
                "text": "دعاهم هود إلى عبادة الله وحده لكنهم استكبروا وقالوا: من أشد منا قوة؟",
                "setting": "desert",
                "chars": ["crowd"],
                "mood": "arrogant",
            },
            {
                "text": "حذرهم هود من عذاب الله وقال: إني أخاف عليكم عذاب يوم عظيم. لكنهم رفضوا.",
                "setting": "desert",
                "chars": ["hud", "crowd"],
                "mood": "warning",
            },
            {
                "text": "أرسل الله عليهم ريحاً صرصراً عاتية سخرها عليهم سبع ليالٍ وثمانية أيام.",
                "setting": "storm",
                "chars": [],
                "mood": "dramatic",
            },
            {
                "text": "دمرت الريح كل شيء وأهلكت قوم عاد، وأنجى الله هوداً والمؤمنين برحمته.",
                "setting": "ruins",
                "chars": ["hud", "believers"],
                "mood": "peaceful",
            },
        ],
    },
    5: {
        "name": "صالح عليه السلام",
        "title": "قصة النبي صالح وناقة الله",
        "color_theme": ((80, 40, 20), (50, 20, 10)),
        "scenes": [
            {
                "text": "بعث الله صالحاً إلى قوم ثمود الذين نحتوا الجبال بيوتاً وكانوا في نعمة عظيمة.",
                "setting": "mountains",
                "chars": ["saleh", "crowd"],
                "mood": "preaching",
            },
            {
                "text": "طلب قوم ثمود آية، فأخرج الله لهم ناقة عظيمة من صخرة صماء معجزة باهرة.",
                "setting": "mountains",
                "chars": ["saleh", "camel", "crowd"],
                "mood": "wonder",
            },
            {
                "text": "قال لهم صالح: هذه ناقة الله لها حق في الشرب، ولا تمسوها بسوء فيأخذكم عذاب.",
                "setting": "mountains",
                "chars": ["saleh", "camel"],
                "mood": "warning",
            },
            {
                "text": "عقر الأشقياء الناقة وتحدّوا أمر الله، فأعطاهم صالح مهلة ثلاثة أيام.",
                "setting": "mountains",
                "chars": ["crowd"],
                "mood": "conflict",
            },
            {
                "text": "جاءت الصيحة فأهلكتهم عن آخرهم، وأنجى الله صالحاً والمؤمنين منه.",
                "setting": "ruins",
                "chars": ["saleh", "believers"],
                "mood": "peaceful",
            },
        ],
    },
    6: {
        "name": "إبراهيم عليه السلام",
        "title": "قصة خليل الله إبراهيم — أبو الأنبياء",
        "color_theme": ((60, 40, 10), (80, 60, 20)),
        "scenes": [
            {
                "text": "إبراهيم خليل الله نشأ في بيئة تعبد الأصنام، لكن عقله الفطري رفض الباطل ووصل للحق.",
                "setting": "village",
                "chars": ["ibrahim"],
                "mood": "thinking",
            },
            {
                "text": "حطّم إبراهيم أصنام قومه وترك الكبير، فلما سألوه قال: بل فعله كبيرهم هذا!",
                "setting": "temple",
                "chars": ["ibrahim", "crowd"],
                "mood": "bold",
            },
            {
                "text": "ألقوه في النار عقاباً، فجعل الله النار برداً وسلاماً عليه — كانت كاليوم الربيعي.",
                "setting": "fire",
                "chars": ["ibrahim"],
                "mood": "miracle",
            },
            {
                "text": "أُمر بذبح ابنه إسماعيل فامتثل، ففداه الله بكبش عظيم وكانت أعظم تضحية.",
                "setting": "desert",
                "chars": ["ibrahim", "ismail"],
                "mood": "sacrifice",
            },
            {
                "text": "بنى إبراهيم وإسماعيل الكعبة المشرفة ودعا: ربنا تقبل منا إنك أنت السميع العليم.",
                "setting": "kaaba",
                "chars": ["ibrahim", "ismail"],
                "mood": "peaceful",
            },
        ],
    },
    7: {
        "name": "يوسف عليه السلام",
        "title": "قصة سيدنا يوسف — أحسن القصص",
        "color_theme": ((60, 10, 60), (40, 5, 80)),
        "scenes": [
            {
                "text": "يوسف بن يعقوب رأى في منامه أحد عشر كوكباً والشمس والقمر يسجدون له.",
                "setting": "night_sky",
                "chars": ["yusuf", "stars"],
                "mood": "wonder",
            },
            {
                "text": "حسده إخوته فألقوه في البئر وأخبروا أباه بأن الذئب أكله — وهم يكذبون.",
                "setting": "well",
                "chars": ["yusuf", "brothers"],
                "mood": "dramatic",
            },
            {
                "text": "اشتراه تجار من مصر فصار في بيت العزيز، وراودته زوجته عن نفسه فاستعصم بالله.",
                "setting": "palace",
                "chars": ["yusuf"],
                "mood": "bold",
            },
            {
                "text": "سُجن ظلماً لسنوات لكنه صبر وعبّر الرؤى، حتى عبّر رؤيا الملك فأُطلق سراحه.",
                "setting": "prison",
                "chars": ["yusuf"],
                "mood": "patient",
            },
            {
                "text": "جعله الملك على خزائن الأرض، وجاء إخوته تائبين فعفا عنهم بكل كرم وسماحة.",
                "setting": "palace",
                "chars": ["yusuf", "brothers"],
                "mood": "happy",
            },
            {
                "text": "جمعه الله بأبيه يعقوب وإخوته وتحققت رؤياه — نهاية أحسن القصص.",
                "setting": "palace",
                "chars": ["yusuf", "family"],
                "mood": "peaceful",
            },
        ],
    },
    8: {
        "name": "موسى عليه السلام",
        "title": "قصة كليم الله موسى وفرعون",
        "color_theme": ((10, 60, 80), (5, 40, 60)),
        "scenes": [
            {
                "text": "ولد موسى في زمن فرعون الذي يقتل أبناء بني إسرائيل، فألقته أمه في اليمّ بوحي الله.",
                "setting": "river",
                "chars": ["baby_moses", "river"],
                "mood": "dramatic",
            },
            {
                "text": "أنقذه آل فرعون وربوه في قصره — هكذا دبّر الله أمره بحكمة بالغة.",
                "setting": "palace",
                "chars": ["moses", "pharaoh"],
                "mood": "wonder",
            },
            {
                "text": "كلّمه الله عند الطور: يا موسى إني أنا الله رب العالمين — واختاره نبياً ورسولاً.",
                "setting": "mountain",
                "chars": ["moses"],
                "mood": "miracle",
            },
            {
                "text": "أرسله الله إلى فرعون بالمعجزات: العصا التي تصير حية، واليد البيضاء المضيئة.",
                "setting": "palace",
                "chars": ["moses", "pharaoh"],
                "mood": "bold",
            },
            {
                "text": "فلق الله البحر لموسى والمؤمنين، فعبروا آمنين وأغرق الله فرعون وجنوده.",
                "setting": "sea",
                "chars": ["moses", "crowd", "pharaoh"],
                "mood": "miracle",
            },
        ],
    },
    9: {
        "name": "سليمان عليه السلام",
        "title": "قصة نبي الله سليمان — ملك الأنبياء",
        "color_theme": ((80, 60, 10), (60, 40, 5)),
        "scenes": [
            {
                "text": "آتى الله سليمان ملكاً عظيماً لم يُؤتَه أحد: منطق الطير وتسخير الجن والريح.",
                "setting": "palace",
                "chars": ["sulayman", "jinn", "birds"],
                "mood": "wonder",
            },
            {
                "text": "كانت جنوده من الإنس والجن والطير يسيرون معاً في نظام بديع.",
                "setting": "field",
                "chars": ["sulayman", "army"],
                "mood": "majestic",
            },
            {
                "text": "أرسل الهدهد برسالة إلى ملكة سبأ بلقيس، فأرسلت هدية فردّها سليمان.",
                "setting": "throne",
                "chars": ["sulayman", "hoopoe"],
                "mood": "wise",
            },
            {
                "text": "أتى بعرش بلقيس في طرفة عين، ودخلت مسلمة لله رب العالمين.",
                "setting": "palace",
                "chars": ["sulayman", "bilqis"],
                "mood": "miracle",
            },
            {
                "text": "قصة سليمان تعلمنا أن الشكر أعظم نعمة، وأن القوة الحقيقية في العدل والتواضع لله.",
                "setting": "palace",
                "chars": ["sulayman"],
                "mood": "peaceful",
            },
        ],
    },
    10: {
        "name": "يونس عليه السلام",
        "title": "قصة النبي يونس — صاحب الحوت",
        "color_theme": ((10, 40, 80), (5, 60, 100)),
        "scenes": [
            {
                "text": "أرسل الله يونس إلى أهل نينوى ليدعوهم، فغضب منهم وانطلق قبل أن يأذن له ربه.",
                "setting": "village",
                "chars": ["yunus", "crowd"],
                "mood": "preaching",
            },
            {
                "text": "ركب السفينة فاضطربت بهم الأمواج، واقترعوا فوقعت القرعة عليه فألقوه في البحر.",
                "setting": "sea",
                "chars": ["yunus", "ship"],
                "mood": "dramatic",
            },
            {
                "text": "التقمه الحوت بأمر الله وصار في ظلمات ثلاث: ظلمة الحوت والبحر والليل.",
                "setting": "deep_sea",
                "chars": ["yunus", "whale"],
                "mood": "dark",
            },
            {
                "text": "نادى في الظلمات: لا إله إلا أنت سبحانك إني كنت من الظالمين. فاستجاب الله له.",
                "setting": "deep_sea",
                "chars": ["yunus"],
                "mood": "prayer",
            },
            {
                "text": "قذفه الحوت للساحل، وأنبت الله عليه شجرة يقطين تظله وهو يستعيد عافيته.",
                "setting": "beach",
                "chars": ["yunus"],
                "mood": "peaceful",
            },
            {
                "text": "أرسله الله ثانية فتاب قوم نينوى كلهم — ومضت القصة معجزة في كتاب الله.",
                "setting": "village",
                "chars": ["yunus", "crowd"],
                "mood": "happy",
            },
        ],
    },
    11: {
        "name": "عيسى عليه السلام",
        "title": "قصة روح الله عيسى المسيح",
        "color_theme": ((60, 80, 100), (40, 60, 80)),
        "scenes": [
            {
                "text": "ولد عيسى من أمه مريم العذراء بأمر الله من غير أب — معجزة تؤكد قدرة الخالق.",
                "setting": "manger",
                "chars": ["maryam", "baby_isa"],
                "mood": "miracle",
            },
            {
                "text": "تكلّم في المهد دفاعاً عن أمه: إني عبد الله آتاني الكتاب وجعلني نبياً.",
                "setting": "village",
                "chars": ["baby_isa", "crowd"],
                "mood": "wonder",
            },
            {
                "text": "أيّده الله بروح القدس وآتاه الإنجيل وعلّمه الكتاب والحكمة والتوراة.",
                "setting": "temple",
                "chars": ["isa"],
                "mood": "teaching",
            },
            {
                "text": "أحيا الموتى بإذن الله، وأبرأ الأكمه والأبرص، وخلق من الطين طيراً فنفخ فيه فطار.",
                "setting": "field",
                "chars": ["isa", "crowd"],
                "mood": "miracle",
            },
            {
                "text": "رفعه الله إليه وحفظه حين دبّر المشركون إيذاءه — وما صلبوه وما قتلوه.",
                "setting": "heaven",
                "chars": ["isa"],
                "mood": "peaceful",
            },
        ],
    },
    12: {
        "name": "محمد ﷺ",
        "title": "قصة خاتم الأنبياء والمرسلين محمد ﷺ",
        "color_theme": ((40, 10, 60), (60, 20, 80)),
        "scenes": [
            {
                "text": "وُلد النبي محمد ﷺ في مكة المكرمة يتيم الأب، ورباه جده ثم عمه، واشتُهر بالأمانة.",
                "setting": "mecca",
                "chars": ["muhammad_child"],
                "mood": "peaceful",
            },
            {
                "text": "في الأربعين نزل عليه جبريل في غار حراء قائلاً: اقرأ. فكانت أولى آيات القرآن الكريم.",
                "setting": "cave",
                "chars": ["muhammad"],
                "mood": "miracle",
            },
            {
                "text": "دعا إلى الإسلام سراً ثم جهاراً، فآذاه قومه وهو صابر لا يتراجع عن دعوته.",
                "setting": "mecca",
                "chars": ["muhammad", "crowd"],
                "mood": "bold",
            },
            {
                "text": "هاجر إلى المدينة المنورة التي صارت عاصمة الإسلام ومنارة العلم والعدل.",
                "setting": "medina",
                "chars": ["muhammad", "believers"],
                "mood": "hopeful",
            },
            {
                "text": "فتح مكة صفحاً وعفواً عمن آذاه — صفحة من أجمل صفحات التاريخ الإنساني.",
                "setting": "mecca",
                "chars": ["muhammad", "crowd"],
                "mood": "majestic",
            },
            {
                "text": "أكمل رسالته وتوفي ﷺ وقد أتم الله الدين ورضي للمسلمين الإسلام دين الرحمة.",
                "setting": "medina",
                "chars": ["believers"],
                "mood": "peaceful",
            },
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


def lerp_color(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def draw_gradient_bg(draw, w, h, top_color, bot_color):
    for y in range(h):
        t = y / h
        color = lerp_color(top_color, bot_color, t)
        draw.line([(0, y), (w, y)], fill=color)


def draw_stars(draw, w, h, count=80, seed=42):
    rng = random.Random(seed)
    for _ in range(count):
        x = rng.randint(0, w)
        y = rng.randint(0, h // 2)
        r = rng.choice([1, 1, 1, 2])
        brightness = rng.randint(180, 255)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(brightness, brightness, brightness))


def draw_ground(draw, w, h, color):
    ground_y = int(h * 0.72)
    draw.rectangle([0, ground_y, w, h], fill=color)


def draw_clouds(draw, w, h, color=(240, 240, 255), count=3, seed=7):
    rng = random.Random(seed)
    for _ in range(count):
        cx = rng.randint(50, w - 50)
        cy = rng.randint(int(h * 0.1), int(h * 0.35))
        for dx, dy, rx, ry in [(0, 0, 60, 35), (-50, 10, 45, 28), (50, 10, 45, 28)]:
            draw.ellipse([cx + dx - rx, cy + dy - ry, cx + dx + rx, cy + dy + ry], fill=color)


def draw_sun(draw, cx, cy, radius, color=(255, 220, 80)):
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color)
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x1 = cx + int((radius + 5) * math.cos(rad))
        y1 = cy + int((radius + 5) * math.sin(rad))
        x2 = cx + int((radius + 18) * math.cos(rad))
        y2 = cy + int((radius + 18) * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=color, width=2)


def draw_moon(draw, cx, cy, radius, color=(255, 240, 180)):
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color)
    draw.ellipse([cx, cy - radius + 4, cx + radius + 4, cy + radius - 4], fill=(20, 20, 60))


def draw_mountain(draw, w, h, color=(100, 80, 60), snow=True):
    pts = [(w // 4, int(h * 0.72)), (w // 2, int(h * 0.18)), (3 * w // 4, int(h * 0.72))]
    draw.polygon(pts, fill=color)
    if snow:
        snow_pts = [(w // 2 - 40, int(h * 0.32)), (w // 2, int(h * 0.18)), (w // 2 + 40, int(h * 0.32))]
        draw.polygon(snow_pts, fill=(240, 240, 250))


def draw_tree(draw, x, y, h_tree=120, color=(34, 100, 34), trunk=(90, 60, 30)):
    trunk_w = 14
    draw.rectangle([x - trunk_w // 2, y - 40, x + trunk_w // 2, y], fill=trunk)
    for i, (dy, rx) in enumerate([(0, 50), (-30, 38), (-58, 24)]):
        draw.polygon([
            (x, y - h_tree + dy - 20),
            (x - rx, y - 40 - dy + 20),
            (x + rx, y - 40 - dy + 20),
        ], fill=color)


def draw_water(draw, w, h, color=(30, 80, 180)):
    water_y = int(h * 0.55)
    draw.rectangle([0, water_y, w, h], fill=color)
    for i in range(3):
        wy = water_y + 15 + i * 18
        for x in range(0, w, 60):
            draw.arc([x, wy - 6, x + 40, wy + 6], 0, 180, fill=(80, 150, 220), width=2)


def draw_whale(draw, cx, cy, w=180, h_body=80, color=(30, 80, 120)):
    draw.ellipse([cx - w // 2, cy - h_body // 2, cx + w // 2, cy + h_body // 2], fill=color)
    tail_pts = [
        (cx + w // 2 - 10, cy),
        (cx + w // 2 + 50, cy - 35),
        (cx + w // 2 + 50, cy + 35),
    ]
    draw.polygon(tail_pts, fill=color)
    draw.ellipse([cx - w // 2 + 10, cy - 12, cx - w // 2 + 34, cy + 12], fill=(220, 220, 240))


def draw_fire(draw, cx, base_y, rng_seed=1):
    rng = random.Random(rng_seed)
    colors = [(255, 80, 0), (255, 160, 0), (255, 220, 80), (200, 40, 0)]
    for layer in range(5):
        color = colors[layer % len(colors)]
        h_flame = 90 - layer * 12
        w_flame = 60 - layer * 6
        pts = [
            (cx, base_y - h_flame),
            (cx - w_flame // 2, base_y),
            (cx + w_flame // 2, base_y),
        ]
        draw.polygon(pts, fill=color)


def draw_ark(draw, cx, cy, color=(139, 90, 43)):
    draw.rectangle([cx - 100, cy - 25, cx + 100, cy + 25], fill=color)
    draw.rectangle([cx - 70, cy - 55, cx + 70, cy - 25], fill=(160, 110, 60))
    draw.rectangle([cx - 20, cy - 70, cx + 20, cy - 55], fill=(120, 80, 40))


def draw_pyramid(draw, cx, cy, size=120, color=(210, 180, 100)):
    pts = [(cx, cy - size), (cx - size, cy + size // 2), (cx + size, cy + size // 2)]
    draw.polygon(pts, fill=color)
    shadow_pts = [(cx, cy - size), (cx + size, cy + size // 2), (cx + size + 20, cy + size // 2)]
    draw.polygon(shadow_pts, fill=(180, 150, 80))


def draw_kaaba(draw, cx, cy, size=100, color=(20, 20, 20)):
    draw.rectangle([cx - size // 2, cy - size, cx + size // 2, cy], fill=color)
    gold = (212, 175, 55)
    draw.rectangle([cx - size // 2, cy - size + 20, cx + size // 2, cy - size + 36], fill=gold)
    draw.rectangle([cx - size // 2, cy - 20, cx + size // 2, cy], fill=gold)


def draw_character(draw, cx, cy, char_type="prophet", color_skin=(220, 180, 140), rng_seed=1):
    rng = random.Random(rng_seed)
    robe_color = {
        "prophet": (200, 200, 255),
        "child": (255, 220, 180),
        "villain": (80, 30, 30),
        "angel": (255, 255, 220),
        "crowd": (150 + rng.randint(0, 80), 130 + rng.randint(0, 60), 100 + rng.randint(0, 60)),
    }.get(char_type, (180, 180, 200))

    body_h = 90
    head_r = 22

    draw.ellipse([cx - 12, cy - body_h - 8, cx + 12, cy - body_h + 8], fill=(200, 150, 80))

    draw.ellipse(
        [cx - head_r, cy - body_h - head_r * 2 - 8, cx + head_r, cy - body_h + head_r * 0 - 8],
        fill=color_skin,
    )

    draw.polygon(
        [(cx, cy - body_h), (cx - 28, cy), (cx + 28, cy)],
        fill=robe_color,
    )

    draw.line([cx - 28, cy - 55, cx - 44, cy - 10], fill=color_skin, width=6)
    draw.line([cx + 28, cy - 55, cx + 44, cy - 10], fill=color_skin, width=6)


def draw_camel(draw, cx, cy, color=(180, 140, 80)):
    draw.ellipse([cx - 50, cy - 30, cx + 50, cy + 30], fill=color)
    draw.ellipse([cx - 60, cy - 50, cx - 20, cy - 10], fill=color)
    draw.ellipse([cx - 15, cy - 65, cx + 5, cy - 30], fill=color)
    for lx in [-30, -10, 15, 35]:
        draw.rectangle([cx + lx, cy + 28, cx + lx + 8, cy + 60], fill=color)
    draw.ellipse([cx - 10, cy - 48, cx + 10, cy - 32], fill=(160, 110, 60))


def draw_hoopoe_bird(draw, cx, cy, color=(180, 120, 40)):
    draw.ellipse([cx - 15, cy - 10, cx + 15, cy + 10], fill=color)
    draw.ellipse([cx + 12, cy - 8, cx + 30, cy + 2], fill=color)
    draw.polygon([(cx + 30, cy - 2), (cx + 42, cy - 2), (cx + 30, cy + 4)], fill=(80, 50, 10))
    for i, fc in enumerate([(255, 80, 0), (255, 160, 0), (255, 200, 80)]):
        draw.polygon([(cx - 5 + i * 4, cy - 10), (cx + 3 + i * 4, cy - 25), (cx + 8 + i * 4, cy - 10)], fill=fc)


def make_scene_background(scene, prophet_data, frame=0):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    top_c, bot_c = prophet_data["color_theme"]
    setting = scene.get("setting", "village")
    mood = scene.get("mood", "peaceful")

    if mood in ("dramatic", "dark", "conflict"):
        top_c = tuple(max(0, c - 40) for c in top_c)
        bot_c = tuple(max(0, c - 40) for c in bot_c)

    draw_gradient_bg(draw, W, H, top_c, bot_c)

    if setting in ("heaven", "paradise"):
        draw_stars(draw, W, H, count=120, seed=frame + 1)
        draw_clouds(draw, W, H, color=(250, 250, 255), count=5, seed=frame)
        draw.rectangle([0, int(H * 0.7), W, H], fill=(150, 220, 150))

    elif setting == "night_sky":
        draw_stars(draw, W, H, count=200, seed=frame + 2)
        draw_moon(draw, W - 120, 90, 50)
        draw.rectangle([0, int(H * 0.7), W, H], fill=(10, 30, 10))

    elif setting in ("garden", "village", "earth"):
        draw_sun(draw, 160, 100, 55)
        draw_clouds(draw, W, H, color=(255, 255, 255), count=4, seed=frame + 3)
        draw.rectangle([0, int(H * 0.7), W, H], fill=(40, 120, 40))
        for tx in [150, 400, 850, 1100]:
            draw_tree(draw, tx, int(H * 0.72), h_tree=110)

    elif setting in ("desert", "ruins"):
        draw_sun(draw, 200, 110, 60)
        draw.rectangle([0, int(H * 0.65), W, H], fill=(200, 160, 80))
        for sx in range(0, W, 120):
            pts = [(sx, int(H * 0.65)), (sx + 60, int(H * 0.65) - 30), (sx + 120, int(H * 0.65))]
            draw.polygon(pts, fill=(180, 140, 60))

    elif setting in ("sea", "flood", "river", "beach"):
        draw_sun(draw, W - 200, 100, 50)
        draw_clouds(draw, W, H, color=(200, 220, 255), count=3)
        draw_water(draw, W, H, color=(20, 80, 180))

    elif setting == "deep_sea":
        draw_gradient_bg(draw, W, H, (5, 20, 80), (2, 10, 40))
        for _ in range(30):
            bx = random.randint(0, W)
            by = random.randint(0, H)
            draw.ellipse([bx, by, bx + 4, by + 4], fill=(80, 120, 200, 100))

    elif setting in ("mountain", "mountains"):
        draw_sun(draw, 150, 100, 50)
        draw_clouds(draw, W, H, color=(240, 240, 255), count=3)
        draw_mountain(draw, W, H, color=(90, 80, 70))
        draw.rectangle([0, int(H * 0.72), W, H], fill=(60, 90, 40))

    elif setting in ("palace", "throne", "temple", "school"):
        draw_sun(draw, W // 2, 90, 45)
        draw.rectangle([0, int(H * 0.7), W, H], fill=(100, 80, 50))
        wall_color = (180, 150, 100) if setting == "palace" else (160, 140, 100)
        draw.rectangle([int(W * 0.15), int(H * 0.25), int(W * 0.85), int(H * 0.7)], fill=wall_color)
        for px in [int(W * 0.2), int(W * 0.4), int(W * 0.6), int(W * 0.8)]:
            draw.rectangle([px - 12, int(H * 0.25), px + 12, int(H * 0.7)], fill=(140, 110, 70))
        draw.rectangle([int(W * 0.35), int(H * 0.48), int(W * 0.65), int(H * 0.7)], fill=(80, 60, 30))

    elif setting == "fire":
        draw_gradient_bg(draw, W, H, (60, 10, 0), (120, 40, 0))
        for fx in [250, 450, 650, 830, 1000]:
            draw_fire(draw, fx, int(H * 0.7), rng_seed=fx)
        draw.rectangle([0, int(H * 0.7), W, H], fill=(40, 20, 0))

    elif setting == "ark_building":
        draw_sun(draw, W - 180, 100, 50)
        draw.rectangle([0, int(H * 0.7), W, H], fill=(80, 60, 30))
        draw_ark(draw, W // 2, int(H * 0.58))

    elif setting == "ark":
        draw_water(draw, W, H, color=(20, 80, 180))
        draw_ark(draw, W // 2, int(H * 0.5))

    elif setting in ("mecca", "medina"):
        draw_sun(draw, W // 2, 80, 50)
        draw.rectangle([0, int(H * 0.65), W, H], fill=(210, 180, 120))
        if setting == "mecca":
            draw_kaaba(draw, W // 2, int(H * 0.65))
        else:
            draw.rectangle([int(W * 0.4), int(H * 0.35), int(W * 0.6), int(H * 0.65)], fill=(200, 180, 140))
            for mx in [int(W * 0.35), int(W * 0.65)]:
                draw.ellipse([mx - 10, int(H * 0.2), mx + 10, int(H * 0.45)], fill=(180, 160, 120))

    elif setting in ("cave", "prison"):
        draw_gradient_bg(draw, W, H, (20, 20, 30), (10, 10, 20))
        draw_stars(draw, W, H, count=80, seed=frame + 5)
        draw.rectangle([0, int(H * 0.65), W, H], fill=(40, 35, 30))
        draw.polygon([
            (int(W * 0.3), int(H * 0.65)),
            (int(W * 0.5), int(H * 0.25)),
            (int(W * 0.7), int(H * 0.65)),
        ], fill=(60, 50, 45))

    elif setting == "kaaba":
        draw_sun(draw, W // 2, 80, 50)
        draw.rectangle([0, int(H * 0.65), W, H], fill=(200, 170, 110))
        draw_kaaba(draw, W // 2, int(H * 0.65))

    elif setting == "manger":
        draw_stars(draw, W, H, count=150, seed=frame + 8)
        draw_moon(draw, W - 100, 80, 45)
        draw.rectangle([0, int(H * 0.7), W, H], fill=(60, 50, 30))
        draw.rectangle([int(W * 0.3), int(H * 0.4), int(W * 0.7), int(H * 0.7)], fill=(100, 80, 50))

    else:
        draw_sun(draw, 160, 100, 50)
        draw_clouds(draw, W, H, count=3)
        draw.rectangle([0, int(H * 0.7), W, H], fill=(40, 100, 40))

    return img, draw


def draw_characters_on_scene(draw, scene, prophet_data, frame=0):
    chars = scene.get("chars", [])
    setting = scene.get("setting", "village")
    ground_y = int(H * 0.72) if setting not in ("sea", "flood", "deep_sea") else int(H * 0.55)

    char_positions = []
    count = len([c for c in chars if c not in ("animals", "stars", "river")])
    if count == 0:
        return
    spacing = min(220, W // (count + 1))
    start_x = W // 2 - spacing * (count - 1) // 2

    idx = 0
    for char in chars:
        cx = start_x + idx * spacing
        cy = ground_y

        if char in ("adam", "noah", "hud", "saleh", "ibrahim", "yusuf", "moses", "sulayman", "yunus", "isa", "muhammad"):
            draw_character(draw, cx, cy, "prophet", color_skin=(220, 180, 140), rng_seed=idx + 1)
            idx += 1
        elif char in ("hawwa", "maryam", "bilqis"):
            draw_character(draw, cx, cy, "prophet", color_skin=(230, 190, 155), rng_seed=idx + 2)
            idx += 1
        elif char in ("iblis", "pharaoh"):
            draw_character(draw, cx, cy, "villain", color_skin=(160, 120, 100), rng_seed=idx + 3)
            idx += 1
        elif char in ("baby_moses", "baby_isa", "muhammad_child"):
            draw_character(draw, cx, cy - 20, "child", color_skin=(230, 190, 155), rng_seed=idx + 4)
            idx += 1
        elif char == "crowd":
            for ci in range(3):
                bx = cx - 50 + ci * 45
                draw_character(draw, bx, cy, "crowd", color_skin=(210 + ci * 5, 170 + ci * 5, 130 + ci * 5), rng_seed=ci + 10 + idx)
            idx += 1
        elif char == "believers":
            for ci in range(2):
                bx = cx - 30 + ci * 55
                draw_character(draw, bx, cy, "crowd", color_skin=(215 + ci * 5, 175 + ci * 5, 135 + ci * 5), rng_seed=ci + 20 + idx)
            idx += 1
        elif char in ("ismail", "brothers", "family"):
            draw_character(draw, cx, cy, "prophet", color_skin=(215, 175, 135), rng_seed=idx + 5)
            idx += 1
        elif char == "camel":
            draw_camel(draw, cx, cy - 30)
            idx += 1
        elif char == "hoopoe":
            draw_hoopoe_bird(draw, cx, cy - 80)
            idx += 1
        elif char == "whale":
            draw_whale(draw, cx, cy - 30)
            idx += 1
        elif char == "ark":
            draw_ark(draw, cx, cy - 20)
            idx += 1
        elif char in ("jinn",):
            draw_character(draw, cx, cy, "villain", color_skin=(100, 140, 120), rng_seed=idx + 6)
            idx += 1
        elif char == "birds":
            draw_hoopoe_bird(draw, cx, cy - 100)
            idx += 1
        elif char == "army":
            for ci in range(4):
                bx = cx - 80 + ci * 50
                draw_character(draw, bx, cy, "crowd", rng_seed=ci + 30 + idx)
            idx += 1


def make_scene_frame(prophet_data, scene, scene_idx, total_scenes):
    img, draw = make_scene_background(scene, prophet_data, frame=scene_idx)
    draw_characters_on_scene(draw, scene, prophet_data, frame=scene_idx)
    return img


def make_title_frame(prophet_data):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    top_c, bot_c = prophet_data["color_theme"]
    draw_gradient_bg(draw, W, H, top_c, bot_c)
    draw_stars(draw, W, H, count=100, seed=99)

    GOLD = (212, 175, 55)
    WHITE = (255, 255, 255)
    LIGHT = (220, 210, 255)

    draw.rectangle([(15, 15), (W - 15, H - 15)], outline=GOLD, width=3)
    draw.rectangle([(25, 25), (W - 25, H - 25)], outline=(100, 80, 160), width=1)

    font_series = load_font(34)
    font_name = load_font(70)
    font_title = load_font(44)
    font_sub = load_font(28)

    def draw_centered(text, font, y, color):
        rendered = render_arabic(text)
        bbox = font.getbbox(rendered)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), rendered, font=font, fill=color)

    draw_centered("✨ قصص الأنبياء الكرتونية ✨", font_series, 70, GOLD)
    draw.line([(80, 135), (W - 80, 135)], fill=GOLD, width=2)
    draw_centered(prophet_data["name"], font_name, 175, WHITE)
    draw_centered(prophet_data["title"], font_title, 295, LIGHT)
    draw.line([(80, 375), (W - 80, 375)], fill=GOLD, width=1)
    draw_centered("مسلسل كرتوني إسلامي للأطفال", font_sub, 410, (180, 160, 220))

    return img


def make_dialogue_frame(prophet_data, scene, scene_idx, total_scenes, line_text):
    base = make_scene_frame(prophet_data, scene, scene_idx, total_scenes)
    draw = ImageDraw.Draw(base)

    GOLD = (212, 175, 55)

    panel_y = int(H * 0.73)
    draw.rectangle([(0, panel_y), (W, H)], fill=(0, 0, 0, 200))
    draw.rectangle([(0, panel_y), (W, panel_y + 3)], fill=GOLD)

    font_dialogue = load_font(36)
    font_counter = load_font(24)

    wrapped = textwrap.wrap(line_text, width=50)
    text_y = panel_y + 18
    for line in wrapped[:3]:
        rendered = render_arabic(line)
        bbox = font_dialogue.getbbox(rendered)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, text_y), rendered, font=font_dialogue, fill=(255, 255, 255))
        text_y += 52

    counter = render_arabic(f"مشهد {scene_idx + 1} من {total_scenes}")
    bbox = font_counter.getbbox(counter)
    draw.text((W - bbox[2] - bbox[0] - 20, panel_y + 8), counter, font=font_counter, fill=GOLD)

    return base


async def generate_prophet_video_async(prophet_num: int, progress_callback=None) -> str:
    prophet = PROPHETS.get(prophet_num)
    if not prophet:
        raise Exception(f"النبي رقم {prophet_num} غير موجود.")

    uid = str(uuid.uuid4())[:8]
    tmp_dir = f"/tmp/prophet_{uid}"
    os.makedirs(tmp_dir, exist_ok=True)

    clips = []
    scenes = prophet["scenes"]
    total_scenes = len(scenes)

    if progress_callback:
        await progress_callback(f"🎨 جاري إنشاء مسلسل قصة {prophet['name']}...")

    title_img = make_title_frame(prophet)
    title_path = f"{tmp_dir}/title.jpg"
    title_img.save(title_path, quality=95)

    title_text = f"مسلسل قصة {prophet['name']} — {prophet['title']}"
    title_audio_path = f"{tmp_dir}/audio_title.mp3"
    tts = gTTS(text=title_text, lang="ar", slow=False)
    tts.save(title_audio_path)
    await asyncio.sleep(0.1)

    title_audio = AudioFileClip(title_audio_path)
    title_clip = ImageClip(title_path).with_duration(title_audio.duration + 1.0)
    title_clip = title_clip.with_audio(title_audio)
    clips.append(title_clip)

    for i, scene in enumerate(scenes):
        if progress_callback:
            await progress_callback(f"🎬 مشهد {i + 1} من {total_scenes}: {scene['mood']}...")

        narration = scene["text"]
        audio_path = f"{tmp_dir}/audio_{i}.mp3"
        tts = gTTS(text=narration, lang="ar", slow=False)
        tts.save(audio_path)
        await asyncio.sleep(0.1)

        audio_clip = AudioFileClip(audio_path)
        duration = max(audio_clip.duration + 1.5, 5.0)

        frame_img = make_dialogue_frame(prophet, scene, i, total_scenes, narration)
        frame_path = f"{tmp_dir}/scene_{i}.jpg"
        frame_img.save(frame_path, quality=95)

        img_clip = ImageClip(frame_path).with_duration(duration)
        img_clip = img_clip.with_audio(audio_clip)
        clips.append(img_clip)

    ending_img = Image.new("RGB", (W, H))
    end_draw = ImageDraw.Draw(ending_img)
    top_c, bot_c = prophet["color_theme"]
    draw_gradient_bg(end_draw, W, H, top_c, bot_c)
    draw_stars(end_draw, W, H, count=150, seed=50)
    GOLD = (212, 175, 55)
    end_draw.rectangle([(15, 15), (W - 15, H - 15)], outline=GOLD, width=3)

    font_end = load_font(60)
    font_sub = load_font(32)
    end_text1 = render_arabic("نهاية المسلسل")
    end_text2 = render_arabic(f"قصة {prophet['name']}")
    end_text3 = render_arabic("اشترك في القناة لمزيد من القصص ✨")

    for text, font, y, color in [
        (end_text1, font_end, 220, (255, 255, 255)),
        (end_text2, font_end, 310, GOLD),
        (end_text3, font_sub, 420, (200, 190, 230)),
    ]:
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        end_draw.text(((W - tw) // 2, y), text, font=font, fill=color)

    ending_path = f"{tmp_dir}/ending.jpg"
    ending_img.save(ending_path, quality=95)
    ending_audio_path = f"{tmp_dir}/audio_ending.mp3"
    tts = gTTS(text=f"نهاية قصة {prophet['name']}. اشترك في القناة لمتابعة قصص الأنبياء.", lang="ar", slow=False)
    tts.save(ending_audio_path)
    await asyncio.sleep(0.1)
    end_audio = AudioFileClip(ending_audio_path)
    end_clip = ImageClip(ending_path).with_duration(end_audio.duration + 1.0)
    end_clip = end_clip.with_audio(end_audio)
    clips.append(end_clip)

    if progress_callback:
        await progress_callback("🎞️ جاري دمج المشاهد في فيديو مسلسل كامل...")

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
        try:
            clip.close()
        except Exception:
            pass
    try:
        final.close()
    except Exception:
        pass

    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return out_path


def get_prophet_list() -> str:
    lines = ["📖 *قصص الأنبياء الكرتونية — اختر نبياً:*\n"]
    for num, data in PROPHETS.items():
        lines.append(f"{num}. {data['name']}")
    lines.append("\n💡 اضغط على رقم النبي لتوليد فيديو مسلسله")
    return "\n".join(lines)
