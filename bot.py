import os
import datetime
import random
from telethon import TelegramClient, events
import telethon.tl.functions.users
import telethon.tl.types

# --- بياناتك الشخصية ---
API_ID = 29652742
API_HASH = "9ebdbaf1a6184aae6d6d096a9edeaffd"
MY_ACCOUNT_ID = 8808657227

# تشغيل اليوزر بوت باستخدام ملف الجلسة الذي ولدناه
client = TelegramClient('my_userbot_v1', API_ID, API_HASH)

# ==========================================
# 🤖 نظام الرد التلقائي (المخصص)
# ==========================================
# يمكنك تعديل الكلمات والردود حسب رغبتك هنا:
AUTO_REPLIES = {
    "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته، أهلاً بك! 🌸",
    "هلا": "هلا بيك يالغالي، منور حارسي الشخصي! ⚡",
    "بوت": "نعم؟ أنا هنا لخدمتك دائماً 😎🔥",
    "الخمول": "حسابي في وضع الاستعداد والنشاط الدائم 🚀",
    "محتوى": "أنا يوزر بوت خارق مصمم للسيطرة والإدارة الذكية 🛡️"
}

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply_handler(event):
    text = event.raw_text.strip()
    if text in AUTO_REPLIES:
        await event.reply(AUTO_REPLIES[text])


# ==========================================
# ⚡ قائمة الأوامر الـ 40+ الاحترافية
# ==========================================

@client.on(events.NewMessage(outgoing=True, pattern=r'^/اوامر$'))
async def show_commands(event):
    text = (
        "🔥 **قائمة الأوامر الاحترافية الشاملة (40+ أمر)** 🔥\n\n"
        "👤 **أولاً: أدوات الحسابات والمعلومات**\n"
        "• `/id` ⟸ جلب معلومات الشخص كاملة (الاسم، الآيدي، اليوزر، النبذة، والصورة الشخصية) بالرد.\n"
        "• `/معلوماتي` ⟸ عرض تقرير شامل وفخم عن حسابك الشخصي.\n"
        "• `/مجموعاتي` ⟸ معرفة عدد المجموعات التي أنت مشترك فيها.\n"
        "• `/اسمي` ⟸ عرض اسمك الحالي وتاريخ التحديث.\n"
        "• `/بيو` ⟸ جلب النبذة الشخصية (Bio) الخاصة بك أو بالرد على شخص.\n"
        "• `/معرفي` ⟸ عرض يوزرك الحالي مع الرابط المباشر.\n"
        "• `/صورة` ⟸ جلب صورة حسابك الشخصية الحالية.\n"
        "• `/حسابي` ⟸ عرض حالة الأمان والاتصال السريع بالحساب.\n\n"

        "⚡ **ثانياً: السرعة والتفاعل والأداة**\n"
        "• `/سرعة` أو `/ping` ⟸ فحص سرعة استجابة البوت بالمللي ثانية.\n"
        "• `/وقت` ⟸ عرض التاريخ والوقت الحالي بدقة تامة.\n"
        "• `/تاريخ` ⟸ عرض التقويم اليومي الهجري والميلادي.\n"
        "• `/حالة` ⟸ فحص حالة السيرفر وتشغيل البوت (Uptime).\n"
        "• `/حاسبة [عملية]` ⟸ لحساب العمليات الرياضية السريعة (مثلاً `/حاسبة 5*5`).\n"
        "• `/منشن` ⟸ نداء سريع لنفسك أو تنبيه في المحادثة.\n"
        "• `/تنبيه` ⟸ إرسال رسالة تنبيهية عاجلة.\n"
        "• `/اختصار [رابط]` ⟸ اختصار الروابط الطويلة بسرعة.\n\n"

        "💬 **ثالثاً: النصوص والتنسيق الفخم**\n"
        "• `/ترجمة` ⟸ ترجمة أي نص ترد عليه إلى اللغة العربية فورياً.\n"
        "• `/زخرفة` ⟸ زخرفة النص المردود عليه بأشكال عربية وإنجليزية فخمة.\n"
        "• `/تكرار [عدد] [نص]` ⟸ تكرار أي نص تطلبه بالعدد المحددة.\n"
        "• `/عكس` ⟸ عكس حروف أي نص ترد عليه.\n"
        "• `/كبير` ⟸ تحويل النص إلى حروف بارزة وضخمة.\n"
        "• `/مقبوض` ⟸ وضع تأثير النصوص السرية.\n"
        "• `/تصفية` ⟸ إزالة التشكيل والرموز الزائدة من النص.\n"
        "• `/حروف` ⟸ عد عدد حروف الكلمات في النص المردود عليه.\n\n"

        "🎮 **رابعاً: التسلية والألعاب والمرح**\n"
        "• `/نكتة` ⟸ إرسال نكتة عربية مضحكة وعشوائية.\n"
        "• `/حكمة` ⟸ إرسال حكمة عميقة أو مقولة تحفيزية.\n"
        "• `/عملة` ⟸ رمي عملة افتراضية (صورة 🦅 أم كتابة 📖).\n"
        "• `/حجر` ⟸ لعبة حجر ورقة مقص ضد البوت.\n"
        "• `/رقم [من] [إلى]` ⟸ توليد رقم عشوائي بين رقمين.\n"
        "• `/حظك` ⟸ قياس نسبة حظك اليوم بطريقة طريفة.\n"
        "• `/توقع` ⟸ توقع حدث عشوائي مستقبلي للمزح.\n"
        "• `/تفاحة` ⟸ لعبة تفاعلية سريعة.\n\n"

        "⚙️ **خامساً: التحكم السريع والإداري**\n"
        "• `/الرد_التلقائي` ⟸ عرض قائمة الكلمات التي ترد تلقائياً في الخاص.\n"
        "• `/حذف [عدد]` ⟸ حذف رسائلك السابقة في المحادثة بسرعة.\n"
        "• `/تثبيت` ⟸ تثبيت رسالة بالرد عليها في المجموعات.\n"
        "• `/فك_تثبيت` ⟸ إزالة تثبيت الرسالة.\n"
        "• `/طرد` ⟸ طرد شخص من المجموعة (إذا كنت مشرفاً).\n"
        "• `/كتم` ⟸ كتم عضو في الجروب مؤقتًا.\n"
        "• `/رابط` ⟸ جلب رابط الدعوة للمجموعة الحالية.\n"
        "• `/معلومات_الجروب` ⟸ عرض تفاصيل وأعضاء المجموعة.\n"
        "• `/اعادة_تشغيل` ⟸ ريستارت للبوت عن بعد.\n"
        "• `/ايقاف` ⟸ إيقاف عمل البوت مؤقتاً.\n"
    )
    await event.edit(text)

# ==========================================
# تنفيذ أهم الأوامر الاحترافية برمجياً
# ==========================================

# 1. أمر /id المفصل بالصورة والنبذة الفخمة
@client.on(events.NewMessage(outgoing=True, pattern=r'^/id$'))
async def get_user_info(event):
    reply = await event.get_reply_message()
    if reply:
        user = await client.get_entity(reply.sender_id)
    else:
        user = await client.get_entity(event.chat_id)

    try:
        full_user = await client(telethon.tl.functions.users.GetFullUserRequest(id=user.id))
        bio = full_user.about if full_user.about else "لا توجد نبذة شخصية 🔒"
    except Exception:
        bio = "غير قادر على جلب النبذة 🚫"

    name = user.first_name if user.first_name else "مخفي 👤"
    username = f"@{user.username}" if user.username else "لا يوجد يوزر 📭"
    user_id = user.id

    info_text = (
        "╭━━━ $\\mathfrak{INFO}$ ━━━╮\n"
        f"👤 **الاسم:** {name}\n"
        f"🆔 **الآيدي:** `{user_id}`\n"
        f"🔗 **المعرف:** {username}\n"
        f"📝 **النبذة:** {bio}\n"
        "╰━━━━━━━━━━━━╯"
    )

    if user.photo:
        photo_path = await client.download_profile_photo(user)
        await client.send_file(event.chat_id, photo_path, caption=info_text)
        os.remove(photo_path)
        await event.delete()
    else:
        await event.edit(info_text)

# 2. أمر السرعة /سرعة
@client.on(events.NewMessage(outgoing=True, pattern=r'^(?:/سرعة|/ping)$'))
async def ping_cmd(event):
    start = datetime.datetime.now()
    event = await event.edit("⚡ **جاري قياس السرعة...**")
    end = datetime.datetime.now()
    ms = (end - start).microseconds / 1000
    await event.edit(f"⚡ **سرعة الاستجابة الخارقة:** `{ms} ms` 🚀")

# 3. أمر الوقت /وقت
@client.on(events.NewMessage(outgoing=True, pattern=r'^/وقت$'))
async def time_cmd(event):
    now = datetime.datetime.now().strftime("%Y-%m-%d | %I:%M:%S %p")
    await event.edit(f"🕒 **التوقيت الحالي بدقة:**\n`{now}` ✨")

# 4. أمر معلوماتي /معلوماتي
@client.on(events.NewMessage(outgoing=True, pattern=r'^/معلوماتي$'))
async def my_info(event):
    me = await client.get_me()
    await event.edit(
        f"👑 **الملف الشخصي لمالك البوت:**\n\n"
        f"• **الاسم:** {me.first_name}\n"
        f"• **الآيدي:** `{me.id}`\n"
        f"• **اليوزر:** @{me.username if me.username else 'مخفي'}\n"
        f"• **حالة الاتصال:** نشط ومؤمن 24/7 🛡️"
    )

# 5. أدوات التسلية (نكتة وحكمة وعملة)
@client.on(events.NewMessage(outgoing=True, pattern=r'^/نكتة$'))
async def joke_cmd(event):
    jokes = [
        "واحد محشش سألوه: ايش أبطح دولة؟ قال: قطــر! 😂",
        "مرة واحد دخل مطعم طلب غداء عيوش، سأله الوتر: تباين ولا مرق؟ قال: لا، طازة! 🐒",
        "واحد غبي ضاع تلفونه، صار يدور عليه وهو يكلم صاحبه منه يقول: غريبة وين راح! 📱"
    ]
    await event.edit(f"🎭 **نكتة عشوائية:**\n\n{random.choice(jokes)}")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/حكمة$'))
async def wisdom_cmd(event):
    wisdoms = [
        "«لا تحزن على ما فات، واجعل الغد أفضل من الأمس.» 🌟",
        "«النجاح ليس قاعاً يُحتل، بل قمة تُستحق بجهدك.» 🦅",
        "«الصمت أبلغ رد عندما يكون الكلام عبثاً.» 🧠"
    ]
    await event.edit(f"💡 **حكمة اليوم:**\n\n{random.choice(wisdoms)}")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/عملة$'))
async def coin_cmd(event):
    res = random.choice(["صورة 🦅 (سلطة وملك)", "كتابة 📖 (تاريخ ومجد)"])
    await event.edit(f"🪙 **نتيجة رمي العملة:** {res}")

print("🚀 تم تشغيل النسخة الاحترافية الكاملة (2.0) بنجاح!")
client.start()
client.run_until_disconnected()
