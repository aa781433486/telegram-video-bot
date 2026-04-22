import json
import os
import random
import asyncio
import base64
import io
import requests

CHANNEL_ID = "@alawodi_10"
SENT_FILE_ALAWODI = "sent_alawodi.json"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ═══════════════════════════════════════════════════════════
# نكت مضحكة جداً — قصيرة ومتوسطة
# ═══════════════════════════════════════════════════════════
JOKES = [
    "😂 واحد اتصل بالطوارئ وقال: جاري يضرب زوجته!\nقالوا: وأنتَ؟\nقال: أنا؟ أصوّر 🎥",

    "🤣 قال المعلم: من يعطيني مثالاً على جملة فيها ماضٍ وحاضر ومستقبل؟\nقال الطالب: كنت جايب صفر وجبت صفر وبجيب صفر 💀",

    "😂 واحد دخل المطعم وطلب: بيضة مسلوقة بدون ملح.\nالنادل: يعني بيضة مسلوقة؟\nقال: لا، اللي معها ملح بالسعر الكامل، واللي بدونها أرخص 🙃",

    "🤣 سأل الأب ابنه: كيف رسبتَ وأنا أدفع لك مصروفاً؟\nقال الابن: وأنت كيف تصير فقيراً وأنا أدفع لا شيء؟ 😭",

    "😂 شخص اشترى مرآة مستعملة. بعد أسبوع رجعها وقال: مريبة، كلما أشوف فيها ألاقي وجه زبون سخيف 😅",

    "🤣 طالب كتب في الامتحان: لا أعرف إجابة هذا السؤال\nالأستاذ صحّح وكتب: وأنا ما أعرف وين المنطق في إجابتك 😂",

    "😄 الأم: قم تعلّم!\nالابن: ما أقدر، فيه ضوضاء.\nالأم: ما فيه أحد غيرنا في البيت!\nالابن: هذا اللي يضايقني، الصمت صاخب 😭",

    "🤣 واحد يبحث عن عمل. سألوه: ما هي نقاط ضعفك؟\nقال: الصدق.\nقالوا: ما نعتبر هذا نقطة ضعف.\nقال: ما يهمني رأيكم 😂",

    "😂 الزوجة: أنت ما تسمعني!\nالزوج: كلامك يدخل من هنا ويطلع من هنا.\nالزوجة: إذن حول أذنيك باتجاهي أكثر! 😵",

    "🤣 سألت أم ابنها الصغير: من أحبّ — أنا أم أبوك؟\nقال: الاثنين.\nقالت: لازم تختار!\nقال: حسناً... أبوي.\nقالت: ليش؟!\nقال: لأنه يكذب أقل 😂",

    "😄 واحد في المستشفى سألوه: فصيلة دمك؟\nقال: ما أتذكر لكن طعمه حامض شوي 🫠",

    "🤣 مدير قال لموظفه: لماذا تأخرت؟\nقال: شفت لافتة مهلاً مدرسة فتمشيت ببطء.\nقال: وأين المدرسة؟\nقال: ما أعرف، بس المدير نفسه ما جاء وقته 😂",

    "😂 واحد يحاول يجي بكير للعمل فكل يوم يجي متأخر. قال المدير: ليش؟\nقال: السيارة ما تشتغل.\nقال: وأمس؟\nقال: اشتغلت وأنا ما صحيت 🤦",

    "🤣 سأل الطبيب: هل تمارس رياضة؟\nقال المريض: أقوم وأجلس طول اليوم.\nقال الطبيب: هذا لا يكفي.\nقال: أقوم وأجلس بسرعة أحياناً! 😭",

    "😂 الابن: أبي أريد أتعلم قيادة السيارة.\nالأب: بكرة.\nالابن: هذا ما قلته السنة اللي فاتت.\nالأب: وسأقوله السنة الجاية أيضاً، البرنامج ثابت 😅",

    "🤣 طالب رسب بكل المواد قال لأبوه: أستاذي يكرهني.\nالأب: ليش؟\nقال: لأني الوحيد اللي يكشف غلطاته قدام الكل 😂",

    "😂 شخص ذهب لمحل ملابس وسأل: عندكم شيء يخليني أبدو أنحف؟\nالبائع: نعم، البُعد عن المحل 🚶",

    "🤣 سأل الزوج: ليش ما ردّيتِ على مكالمتي؟\nقالت الزوجة: شفت اسمك على الشاشة وقررت أستريح 😂",

    "😄 مريض قال للطبيب: عندي ذاكرة ضعيفة جداً.\nالطبيب: منذ متى؟\nقال: منذ متى ماذا؟ 😵",

    "🤣 معلمة سألت: من اخترع الهاتف؟\nقال الطالب: ما أدري لكن أكيد ما اخترع إيقاف الصوت 😂",

    "😂 شخص اتصل بالمطعم: هل عندكم أرجل دجاج؟\nقالوا: نعم.\nقال: كيف تمشون إذن؟ 🤣",

    "🤣 قال الأب: غداً أشتري لك ألعاب.\nالابن: وعدتني هذا الأسبوع الماضي!\nالأب: وسأعدك الأسبوع القادم أيضاً، الوعود متجددة 😭",

    "😂 الأستاذ: من يعرف كمية الماء في جسم الإنسان؟\nالطالب: لا أعرف لكن عندما أبكي يبدو أنها لا نهائية 😂",

    "🤣 موظف سأل مديره: هل سترفعني هذا العام؟\nقال المدير: إذا رفعك شخص واحد كان كافياً! 😵",

    "😄 الابن: أمي، صاحبي يقول أن والده يأخذ المصروف من أمه.\nالأم: وماذا قلت له؟\nقال: قلت بيتنا مختلف، عندنا ما فيه مصروف أصلاً 😂",

    "🤣 سأل الطالب الأستاذ: هل يمكن معاقبتي على شيء لم أفعله؟\nقال الأستاذ: لا طبعاً.\nقال: ممتاز، لم أفعل الواجب 😂",

    "😂 شخص اشترى ساعة وقال للبائع: هذه الساعة وقفت!\nقال البائع: طبيعي، الوقت يمر، الساعة لا 😅",

    "🤣 رجل قال لزوجته: يا حبيبتي، حبّي لكِ كالبحر.\nقالت: عميق؟\nقال: لا، ملحه وما يُشرب منه 😂",

    "😂 الأم: لماذا تبكي؟\nالابن: أبي ضربني.\nالأم: لماذا لم تقل لي؟\nالابن: لأنك ستضربيني أكثر 🤣",

    "🤣 طبيب قال لمريض: عليك تناول هذه الحبوب مدى الحياة.\nقال المريض: لكنك وصفت لي ثلاث حبوب فقط!\nقال الطبيب: أعرف 💀",

    "😂 واحد اشترى كتاباً: كيف تتوقف عن التسويف.\nمضى عليه عام ولم يفتحه حتى الآن 😅",

    "🤣 الزوج: طبختِ اليوم؟\nالزوجة: آه!\nالزوج: ليش ريحة الأكل مش موجودة؟\nالزوجة: طبختُ البارحة 😭",

    "😂 سألت امرأة طبيبها: هل يجوز تناول المضاد الحيوي مع القهوة؟\nقال: نعم.\nقالت: وماذا عن الشوكولاتة؟\nقال: يا ستي خذي الدواء مع أي شيء وسامحيني 😂",

    "🤣 مدير سأل موظفه: هل تعرف لماذا استدعيتك؟\nقال الموظف: لا.\nقال المدير: هذا هو المشكلة، لا تعرف شيئاً 😵",

    "😄 شخص نام مبكراً ثم قال: نمت مبكراً كما نصحك الأطباء!\nصاحبه: وفعلت شيئاً مفيداً؟\nقال: نعم، استيقظت ناعساً مبكراً أيضاً 🤣",

    "🤣 سأل الأستاذ: ما هو أطول نهر في العالم؟\nقال الطالب: النهر الذي تشرحه أنت يا أستاذ 😂",

    "😂 الأب: ابني، الفلوس ما تجيب السعادة.\nالابن: صح، بس تجيب الطعام، والطعام يجيب السعادة 🎯",

    "🤣 موظف سأل: هل الراتب آخر الشهر؟\nالمدير: نعم.\nقال: وهل الشهر القادم أيضاً سيأتي؟\nقال: إن شاء الله.\nقال: الله يسهّل 😭",

    "😂 طالب قال لأستاذه: لم أفهم الدرس.\nقال الأستاذ: منذ البداية؟\nقال: منذ دخلت المدرسة عام 2015 😵",

    "🤣 واحد اشترى عطر وقال: هذا العطر يدوم 24 ساعة.\nبعد ساعتين راح العطر.\nرجع للبائع: قلت 24 ساعة!\nقال: أيوه، 24 ساعة على الرف 😂",

    "😂 مريض سأل الطبيب: حالتي خطيرة؟\nالطبيب: لا، ستعيش طويلاً.\nقال: وأنت كيف تعرف؟\nقال: لأن كل المرضى الخطيرين يموتون أولاً 😅",

    "🤣 ابن قال لأبيه: أعطني مليون دولار.\nقال الأب: وماذا تعطيني؟\nقال: شكراً.\nقال الأب: أرخص منك اشتري شكراً 😂",

    "😄 سألت امرأة رجلاً: لماذا لم تتزوج حتى الآن؟\nقال: كنت في انتظار المرأة المثالية.\nقالت: ووجدتها؟\nقال: نعم، لكنها كانت تنتظر الرجل المثالي 💀",

    "🤣 طفل سأل: أبا، لماذا نرمي سن اللبن للسقف؟\nقال: حتى يكبر الأطفال.\nقال: وإذا سقط على رأسي؟\nقال: ستكبر أسرع 😂",

    "😂 شخص قال لصديقه: أنا نمت ثماني ساعات ومستمر نعسان.\nصديقه: ربما تحتاج تسع.\nقال: جربت عشر، ما فرق.\nالصديق: جرب لا تنام أصلاً.\nقال: هذا ما أفعله في العمل 😵",

    "🤣 في امتحان: المعلم: ابن عمر أين أنت؟\nبعد صمت: هنا يا أستاذ.\nقال: وين؟ ما أراك!\nقال: تحت المقعد، أبحث عن قلمي 😂",

    "😂 سألت الزوجة: متى آخر مرة أخبرتني أنني جميلة؟\nقال الزوج: البارحة في المنام 😅",

    "🤣 طفل سأل أمه: ما معنى الكذب؟\nقالت: حين تقول شيئاً غير حقيقي.\nقال: مثل حين تقولين لأبي إن الأكل سيكون جاهزاً بعد خمس دقائق؟ 💀",

    "😂 واحد دخل على دكتور وقال: أشعر بألم في كل مكان.\nالدكتور: أشِر إلى المكان المؤلم.\nأشار إلى كل جسمه.\nقال الدكتور: إصبعك مكسور 😂",

    "🤣 شخص رأى لافتة: ممنوع الوقوف تحت الأشجار في العاصفة.\nوقف تحتها وقال: ما فيه عاصفة الحين 🌩️",

    "😄 الطالب: أستاذ، هل يمكن معاقبة شخص على شيء لم يفكر فيه؟\nالأستاذ: بالطبع لا.\nالطالب: ممتاز، لم أفكر في الواجب أصلاً 😂",
]

# ═══════════════════════════════════════════════════════════
# عبارات خيالية وحكم عقلانية حادة
# ═══════════════════════════════════════════════════════════
QUOTES = [
    "الفرق بين الشخص الناجح والفاشل ليس في الموهبة...\nبل في من يقوم من السقطة ويكمل، ومن يجلس ويعدّ الجروح 🔥",

    "أخطر ما يمكن أن تفعله:\nأن تُعطي وقتك لمن لا يرى قيمتك — الوقت لا يُسترد، والأشخاص يُستبدلون ⏳",

    "العقل كالبحر...\nكلما غصت فيه وجدت كنوزاً، وكلما بقيت على السطح رأيت فقط الأمواج 🐚",

    "الحكمة الحقيقية ليست في معرفة كل الإجابات...\nبل في معرفة الأسئلة الصحيحة التي تستحق أن تُسأل 🧠",

    "الناجحون لا يختلفون عنك في القدرات...\nيختلفون في أنهم يبدؤون قبل أن يكونوا مستعدين تماماً 💪",

    "أجمل الأشياء في الحياة تأتي بعد أصعب اللحظات...\nالفجر لا يأتي إلا بعد أحلك ساعات الليل 🌅",

    "لا تضع طاقتك في من لا يستحق وقتك...\nالشمعة التي تحترق لتضيء الظلام لا تحترق في وضح النهار 🕯️",

    "الفشل ليس نقيض النجاح...\nالفشل جزء من النجاح، وكل من يخبرك بغير ذلك لم ينجح حقاً بعد 🏆",

    "الهدوء ليس ضعفاً...\nبل هو القوة التي تعرف متى تصمت ومتى تتكلم، ومتى تبتسم أمام من يريد رؤيتك تنهار 😌",

    "الشخص الذي يضيء حياة الآخرين...\nلا يمكن أن يبقى في الظلام طويلاً — الكون منصف 🌟",

    "الأسد لا يلتفت لنباح الكلاب...\nركّز على هدفك ولا تُضيّع طاقتك على من يريدون إيقافك 👑",

    "التغيير الحقيقي يبدأ حين تدرك...\nأن المشكلة الوحيدة التي تستحق حلها هي تلك التي تحملها في داخلك 🪞",

    "كن كالماء: لا شكل محدد، لكن قادر على اختراق أصلب الحجارة...\nالمثابرة تهزم الصلابة دائماً 💧",

    "حياتك لوحة فنية...\nولا أحد يملك فرشاتك غيرك — فلا تدع أحداً يرسم مكانك 🖌️",

    "أذكى قرار يمكن أن تتخذه هو الابتعاد عن:\nمن يسرق طاقتك، ومن يزرع الشك في نفسك، ومن يجعلك تعتذر على وجودك ✂️",

    "الليل يعلّمنا أن الظلام مؤقت...\nوالنجوم لا تظهر إلا حين يشتد الظلام ✨",

    "الضغط يصنع الألماس...\nفإذا كنت تمر بضغط شديد، فأنت في طريقك لتصبح شيئاً لا يُكسر 💎",

    "المستقبل لا يُبنى بالتمني...\nيُبنى بقرارات صعبة تتخذها اليوم بينما الجميع يريحون 🏗️",

    "السعادة الحقيقية:\nأن تنام بلا خوف، تصحو بلا ندم، وتعيش بلا قناع 😊",

    "الوقت لا يُعيد ما مضى...\nلكنه يمنحك كل يوم ورقة بيضاء جديدة — السؤال: ماذا ستكتب؟ 📝",

    "التحول لا يحدث في لحظة مريحة...\nالفراشة تتألم داخل الشرنقة، لكنها تخرج قادرة على الطيران 🌸",

    "الناس من حولك إما يمنحونك طاقة أو يسرقونها...\nاختر بيئتك كما تختار هواءك — حياتك تعتمد عليه 🌬️",

    "التواضع ليس تقليلاً من قدرك...\nبل هو الثقة الكافية بنفسك بحيث لا تحتاج لإثباتها لأحد 👑",

    "الشخص الذي يعرف لماذا يعمل...\nيتحمل أي كيف ويتجاوز أي عقبة بلا شكوى 💪",

    "القوة الحقيقية ليست في عدم الخوف...\nبل في أن تخاف وتمضي رغم ذلك — هذا هو الشجاع الحقيقي 🦁",

    "كل صباح هو رسالة من الكون تقول:\nلديك فرصة أخرى، استخدمها بحكمة 🌄",

    "الحياة لغز، والناجح هو من يتعامل مع القطع الناقصة بإبداع...\nلا بانتظار من يكملها له 🎲",

    "أغلى ما تملك ليس في حسابك البنكي...\nبل في قيمك التي لا يمكن لأحد شراؤها 🏦",

    "البحر لا يعتذر للأمواج على قوته...\nكن صادقاً مع طبيعتك ولا تُلطّف نفسك لمن لا يقدر عمقك 🌊",

    "الذكاء الحقيقي:\nأن تعرف ما لا يجب أن تقوله، وما لا يجب أن تفعله، وما لا يجب أن تفكر فيه 🧠",

    "أصعب لحظة في الحياة ليست حين تسقط...\nبل حين تقرر النهوض وحيداً أمام من ظن أنك لن تقوم 💪",

    "النجوم لا تتنافس مع القمر...\nكلٌّ يضيء بطريقته — التنافس الحقيقي هو مع نفسك فقط ✨",
]

# ═══════════════════════════════════════════════════════════
# بروموبتات توليد الخلفيات بالذكاء الاصطناعي — جودة عالية
# ═══════════════════════════════════════════════════════════
WALLPAPER_PROMPTS = [
    ("الفضاء السحري", "A stunning 4K galaxy wallpaper with swirling blue and gold nebulae, thousands of glittering stars cascading like rain, and a transparent crystal planet reflecting a thousand colors. Cinematic, ultra-detailed, hyperrealistic space art."),
    ("غابة الكريستال", "A breathtaking 4K wallpaper of a crystal forest at night, transparent glass trees shimmering with rainbow light under a full moon, soft white mist drifting between the trunks. Fantasy art, ultra HD."),
    ("مدينة السحاب", "An epic 4K wallpaper of a futuristic floating city above golden clouds, coral glass towers, neon blue and purple lights illuminating the sky. Cinematic, hyper-detailed concept art."),
    ("أسد الضوء", "A majestic 4K wallpaper of a giant lion made entirely of glowing cosmic light, its mane formed from solar flares, eyes burning like stars, against a deep space background. Epic digital art, ultra HD."),
    ("حديقة الياقوت", "A magical 4K wallpaper of an enchanted garden where roses are ruby red gemstones, leaves are emerald crystals, and glowing butterflies made of light hover in golden air. Fantasy fine art, ultra-detailed."),
    ("تنين الجليد", "A breathtaking 4K wallpaper of an ice dragon soaring over snowy mountains, its wings reflecting aurora borealis in green and violet. Cinematic, hyper-realistic fantasy art."),
    ("المحيط الكوني", "A stunning 4K wallpaper of a cosmic ocean where each wave is a universe, luminous fish swimming between galaxies, swirling nebulae below the surface. Surreal space art, ultra HD."),
    ("مدينة البرق", "A dramatic 4K wallpaper of a futuristic city under a lightning storm, every bolt illuminating silver skyscrapers, streets flowing with rivers of electric blue light. Cinematic concept art, ultra HD."),
    ("عقاب الفجر", "A powerful 4K wallpaper of a royal eagle with golden flame wings soaring over a pink sunrise, ancient city awakening below. Epic digital painting, ultra-detailed."),
    ("قصر القمر", "A dreamlike 4K wallpaper of a grand palace on the moon's surface, towers stretching to touch the stars, silver light gates pulsing like a heartbeat. Fantasy art, cinematic quality."),
    ("حضارة الغابة", "A lush 4K wallpaper of an advanced civilization grown inside a tropical rainforest, buildings of living wood and vines, rivers of green light flowing between giant trees. Concept art, ultra HD."),
    ("فينيق الأبدية", "A majestic 4K wallpaper of a phoenix rising from ashes in brilliant orange, red, and gold flames, behind it a sky of embers and hope. Epic fantasy digital art, ultra-detailed."),
    ("وادي النجوم", "A magical 4K wallpaper of a deep valley where stars fall like a waterfall, trees catching stars in their leaves and turning them into glowing green light. Fantasy art, ultra HD."),
    ("الجبل الأزلي", "A breathtaking 4K wallpaper of a colossal mountain piercing the clouds, its peak touching space, a giant crystal at the summit gathering cosmic light and reflecting it across the world. Cinematic, ultra-detailed."),
    ("جسر الأكوان", "An epic 4K wallpaper of an infinite rainbow bridge spanning between multiple planets, beings of light walking towards an unseen horizon. Cosmic surreal art, ultra HD."),
    ("حوت الغيوم", "A dreamy 4K wallpaper of a giant whale swimming through a sea of soft white clouds, its fins touching stars, eyes like twin moons. Fantasy digital art, ultra-detailed."),
    ("روضة الجنة", "A luminous 4K wallpaper of a paradisiacal garden where flowers bloom from light, each blossom a tiny world, waves of color rising like fragrance. Fine art fantasy, ultra HD."),
    ("محارب الكوني", "An epic 4K wallpaper of a cosmic warrior standing at the edge of a galaxy, armor forged from stars, sword of pure light cutting through infinite darkness. Cinematic concept art, ultra HD."),
    ("عاصمة تحت الماء", "A stunning 4K wallpaper of an elegant underwater city in turquoise water, coral towers, colorful fish flying around like birds. Fantasy concept art, ultra-detailed."),
    ("انفجار الكون", "A spectacular 4K wallpaper capturing the moment of the Big Bang — an explosion of light, color, and energy, every spark a new universe being born. Cosmic abstract art, ultra HD."),
    ("غروب الذهب", "A breathtaking 4K wallpaper of a golden sunset over a desert of liquid gold dunes, the sky painted in layers of amber, rose, and deep violet. Photorealistic landscape, ultra HD."),
    ("مدينة المستقبل", "A cinematic 4K wallpaper of a futuristic megacity at night, holographic advertisements floating above sleek towers, flying vehicles streaking through glowing skyways. Ultra-detailed sci-fi concept art."),
    ("قمة الجليد", "A dramatic 4K wallpaper of snow-capped mountain peaks emerging above a sea of clouds at sunrise, golden light breaking through the mist. Photorealistic nature photography style, ultra HD."),
    ("غابة الخريف", "A magical 4K wallpaper of an autumn forest with trees of fire — crimson, amber, and gold leaves glowing as if lit from within, a mist-covered path leading into the unknown. Ultra-detailed digital art."),
    ("بحر الأحلام", "A surreal 4K wallpaper of a calm ocean at night reflecting a sky full of stars, the horizon blending seamlessly between water and cosmos. Photorealistic dreamscape, ultra HD."),
]


# ═══════════════════════════════════════════════════════════
# توليد صورة AI حقيقية عبر Imagen
# ═══════════════════════════════════════════════════════════

def generate_wallpaper_image(prompt: str) -> bytes | None:
    if not GOOGLE_API_KEY:
        return None
    try:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"imagen-3.0-generate-002:predict?key={GOOGLE_API_KEY}"
        )
        body = {
            "instances": [{"prompt": prompt}],
            "parameters": {"sampleCount": 1, "aspectRatio": "9:16"},
        }
        resp = requests.post(url, json=body, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        b64 = data["predictions"][0]["bytesBase64Encoded"]
        return base64.b64decode(b64)
    except Exception as e:
        print(f"⚠️ فشل توليد الصورة: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# منطق عدم التكرار
# ═══════════════════════════════════════════════════════════

def _load_sent() -> dict:
    if not os.path.exists(SENT_FILE_ALAWODI):
        return {"jokes": [], "quotes": [], "wallpapers": []}
    try:
        with open(SENT_FILE_ALAWODI, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {"jokes": [], "quotes": [], "wallpapers": []}
            return data
    except Exception:
        return {"jokes": [], "quotes": [], "wallpapers": []}


def _save_sent(data: dict):
    with open(SENT_FILE_ALAWODI, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _pick_unsent(pool: list, sent_indices: list, need: int) -> list:
    total = len(pool)
    unsent = [i for i in range(total) if i not in sent_indices]
    if len(unsent) < need:
        half = total // 2
        keep = sent_indices[-half:] if len(sent_indices) >= half else sent_indices
        unsent = [i for i in range(total) if i not in keep]
    return random.sample(unsent, min(need, len(unsent)))


def pick_content_alawodi(count: int = 10) -> list:
    sent = _load_sent()
    jokes_sent = sent.get("jokes", [])
    quotes_sent = sent.get("quotes", [])
    wallpapers_sent = sent.get("wallpapers", [])

    n_jokes = max(1, round(count * 0.25))
    n_content = count - n_jokes
    n_quotes = round(n_content * 0.55)
    n_wallpapers = n_content - n_quotes

    joke_picks = _pick_unsent(JOKES, jokes_sent, n_jokes)
    quote_picks = _pick_unsent(QUOTES, quotes_sent, n_quotes)
    wall_picks = _pick_unsent(WALLPAPER_PROMPTS, wallpapers_sent, n_wallpapers)

    jokes_sent.extend(joke_picks)
    quotes_sent.extend(quote_picks)
    wallpapers_sent.extend(wall_picks)

    if len(jokes_sent) > len(JOKES) * 2:
        jokes_sent = jokes_sent[-len(JOKES):]
    if len(quotes_sent) > len(QUOTES) * 2:
        quotes_sent = quotes_sent[-len(QUOTES):]
    if len(wallpapers_sent) > len(WALLPAPER_PROMPTS) * 2:
        wallpapers_sent = wallpapers_sent[-len(WALLPAPER_PROMPTS):]

    _save_sent({"jokes": jokes_sent, "quotes": quotes_sent, "wallpapers": wallpapers_sent})

    items = (
        [("joke", JOKES[i]) for i in joke_picks]
        + [("quote", QUOTES[i]) for i in quote_picks]
        + [("wallpaper", WALLPAPER_PROMPTS[i]) for i in wall_picks]
    )
    random.shuffle(items)
    return items


# ═══════════════════════════════════════════════════════════
# النشر الرئيسي
# ═══════════════════════════════════════════════════════════

async def post_to_alawodi_channel(bot, count: int = 10) -> int:
    items = pick_content_alawodi(count)
    sent_count = 0

    for kind, content in items:
        try:
            if kind == "wallpaper":
                title, prompt = content
                caption = f"🖼️ خلفية AI | {title}\n\n🤖 صورة مولّدة بالذكاء الاصطناعي\n#خلفية_AI #ذكاء_اصطناعي"
                img_bytes = await asyncio.get_event_loop().run_in_executor(
                    None, generate_wallpaper_image, prompt
                )
                if img_bytes:
                    await bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=io.BytesIO(img_bytes),
                        caption=caption,
                    )
                    sent_count += 1
                else:
                    await bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=f"🖼️ خلفية AI | {title}\n\n{prompt[:200]}",
                    )
                    sent_count += 1
            else:
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=content,
                )
                sent_count += 1
        except Exception as e:
            print(f"⚠️ خطأ في إرسال رسالة لقناة العوادي: {e}")

        await asyncio.sleep(3)

    print(f"✅ تم إرسال {sent_count} رسائل إلى {CHANNEL_ID}")
    return sent_count
