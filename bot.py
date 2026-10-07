# ==============================================================================
# 🌟 المشروع الأسطوري: اليوزر بوت الفخم والضخم (Mega Userbot v3.0 - Cloud Ready)
# ==============================================================================

import os
import sys
import time
import datetime
import random
import asyncio
import math
from telethon import TelegramClient, events, Button
import telethon.tl.functions.users
import telethon.tl.types
import telethon.tl.functions.channels
import telethon.tl.functions.messages

# --- إعدادات الحساب الأساسية ---
API_ID = 29652742
API_HASH = "9ebdbaf1a6184aae6d6d096a9edeaffd"
MY_ACCOUNT_ID = 8808657227

# استخدام ملف الجلسة المحلي الموجود في المستودع مباشرة لتجنب مشاكل المتغيرات
client = TelegramClient('my_userbot_v1', API_ID, API_HASH)

# --- الهياكل ومتغيرات الحالة العامة ---
CUSTOM_AUTO_REPLY = {"text": None}
STOP_SPAM = {"status": False}
BOT_START_TIME = datetime.datetime.now()

# قاموس الزخارف العربية والإنجليزية الفخمة
ARABIC_DECORATIONS = {
    "1": lambda t: f"『 {t} 』",
    "2": lambda t: f"★[ {t} ]★",
    "3": lambda t: f"卍 {t} 卍",
    "4": lambda t: f"『✦』 {t} 『✦』",
    "5": lambda t: f"【 {t} 】"
}

ENGLISH_DECORATIONS = {
    "1": lambda t: "".join(chr(ord(c) + 119735) if 'a' <= c <= 'z' else (chr(ord(c) + 119729) if 'A' <= c <= 'Z' else c) for c in t),
    "2": lambda t: "".join(chr(ord(c) + 120119) if 'a' <= c <= 'z' else (chr(ord(c) + 120113) if 'A' <= c <= 'Z' else c) for c in t),
    "3": lambda t: f"𝒯:: {t} ::𝒯",
    "4": lambda t: f"✨ ⦋ {t} ⦃ 🌟 ⦄ ⦊ ✨"
}


# ==============================================================================
# القسم الأول: نظام الرد التلقائي والأوفلاين الذكي
# ==============================================================================

@client.on(events.NewMessage(outgoing=True, pattern=r'^/اضافة_رد_تلقائي (.*)$'))
async def set_custom_reply(event):
    await event.delete()
    new_text = event.pattern_match.group(1).strip()
    CUSTOM_AUTO_REPLY["text"] = new_text
    await client.send_message(
        event.chat_id, 
        f"✅ **تمت برمجة وتفعيل الرد التلقائي بنجاح!**\n\n💬 **النص المعتمد:**\n`{new_text}`"
    )

@client.on(events.NewMessage(outgoing=True, pattern=r'^/حذف_رد_تلقائي$'))
async def delete_custom_reply(event):
    await event.delete()
    CUSTOM_AUTO_REPLY["text"] = None
    await client.send_message(event.chat_id, "🗑️ **تم مسح وإلغاء الرد التلقائي بالكامل.**")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/الرد_التلقائي$'))
async def show_custom_reply(event):
    await event.delete()
    current = CUSTOM_AUTO_REPLY.get("text")
    if current:
        await client.send_message(event.chat_id, f"📋 **الرد التلقائي المفعل حالياً:**\n\n`{current}`")
    else:
        await client.send_message(event.chat_id, "📭 لا يوجد أي رد تلقائي مسجل حالياً.")

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def offline_auto_reply_engine(event):
    try:
        reply_text = CUSTOM_AUTO_REPLY.get("text")
        if not reply_text:
            return
        me = await client.get_me()
        is_offline = isinstance(me.status, (telethon.tl.types.UserStatusOffline, telethon.tl.types.UserStatusRecently))
        if is_offline and event.raw_text.strip():
            await event.reply(reply_text)
    except Exception as e:
        print(f"Error in auto-reply: {e}")


# ==============================================================================
# القسم الثاني: النظام التفاعلي الخرافي (الزخرفة والترجمة بالأزرار الشفافة)
# ==============================================================================

@client.on(events.NewMessage(outgoing=True, pattern=r'^/زخرفة(?:\s+(.*))?$'))
async def decorate_menu(event):
    await event.delete()
    text = event.pattern_match.group(1)
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text
        else:
            await client.send_message(event.chat_id, "⚠️ **خطأ:** اكتب النص بعد الأمر أو رد على رسالة لزخرفتها!\nمثال: `/زخرفة السلام عليكم`")
            return

    buttons = [
        [Button.inline("🌟 إنجليزية فخمة (1)", data=f"dec_en_1_{text}"), Button.inline("💎 إنجليزية دائرية (2)", data=f"dec_en_2_{text}")],
        [Button.inline("✨ إنجليزية أقواس (3)", data=f"dec_en_3_{text}"), Button.inline("💫 إنجليزية نجوم (4)", data=f"dec_en_4_{text}")],
        [Button.inline("🔥 عربية ملكية (1)", data=f"dec_ar_1_{text}"), Button.inline("⭐ عربية نجوم (2)", data=f"dec_ar_2_{text}")],
        [Button.inline("⚔️ عربية سيوف (3)", data=f"dec_ar_3_{text}"), Button.inline("🛡️ عربية فاخرة (4)", data=f"dec_ar_4_{text}")]
    ]
    await client.send_message(
        event.chat_id, 
        f"🎴 **لوحة التحكم بالزخرفة الاحترافية:**\n📌 **النص المستهدف:** `{text}`\n\nاختر نوع الزخرفة المطلوبة من الأزرار أدناه:", 
        buttons=buttons
    )

@client.on(events.CallbackQuery(pattern=r'^dec_'))
async def decorate_callback(event):
    try:
        data = event.data.decode('utf-8')
        parts = data.split('_', 3)
        lang_type = parts[1]
        dec_idx = parts[2]
        text = parts[3]

        if lang_type == "en":
            if dec_idx == "1":
                result = ENGLISH_DECORATIONS["1"](text)
            elif dec_idx == "2":
                result = ENGLISH_DECORATIONS["2"](text)
            elif dec_idx == "3":
                result = ENGLISH_DECORATIONS["3"](text)
            else:
                result = ENGLISH_DECORATIONS["4"](text)
        else:
            if dec_idx == "1":
                result = ARABIC_DECORATIONS["1"](text)
            elif dec_idx == "2":
                result = ARABIC_DECORATIONS["2"](text)
            elif dec_idx == "3":
                result = ARABIC_DECORATIONS["3"](text)
            else:
                result = ARABIC_DECORATIONS["5"](text)

        await event.edit(f"✅ **تمت الزخرفة بنجاح:**\n\n`{result}`")
    except Exception as e:
        await event.answer(f"حدث خطأ: {e}", alert=True)


@client.on(events.NewMessage(outgoing=True, pattern=r'^/ترجمة(?:\s+(.*))?$'))
async def translate_menu(event):
    await event.delete()
    text = event.pattern_match.group(1)
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text
        else:
            await client.send_message(event.chat_id, "⚠️ **خطأ:** رد على رسالة بـ `/ترجمة` أو اكتب النص بجانبه فوراً!")
            return

    buttons = [
        [Button.inline("🌐 الترجمة الفورية إلى العربية (AR)", data=f"tr_ar_{text}")],
        [Button.inline("🇺🇸 Translate to English (EN)", data=f"tr_en_{text}")],
        [Button.inline("🇫🇷 Traduire en Français (FR)", data=f"tr_fr_{text}")],
        [Button.inline("🇪🇸 Traducir al Español (ES)", data=f"tr_es_{text}")]
    ]
    await client.send_message(
        event.chat_id, 
        f"🔍 **مركز الترجمة العالمي المتقدم:**\n📌 **النص الأصلي:** `{text}`\n\nحدد لغة الترجمة المستهدفة:", 
        buttons=buttons
    )

@client.on(events.CallbackQuery(pattern=r'^tr_'))
async def translate_callback(event):
    try:
        data = event.data.decode('utf-8')
        parts = data.split('_', 2)
        lang = parts[1]
        text = parts[2]

        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source='auto', target=lang).translate(text)
        
        await event.edit(f"🌐 **النتيجة المترجمة ({lang.upper()}):**\n\n`{translated}`")
    except Exception as e:
        await event.answer(f"تأكد من تثبيت مكتبة deep-translator:\nخطأ: {e}", alert=True)


# ==============================================================================
# القسم الثالث: أدوات الحسابات والمعلومات الشاملة (/id وغيرها)
# ==============================================================================

@client.on(events.NewMessage(outgoing=True, pattern=r'^/id$'))
async def get_user_info(event):
    await event.delete()
    try:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id) if reply else await client.get_entity(event.chat_id)
        full_user = await client(telethon.tl.functions.users.GetFullUserRequest(id=user))
        bio = full_user.about if full_user.about else "لا توجد نبذة شخصية (Bio) 🔒"
    except Exception:
        bio = "غير متاحة أو مخفية بالخصوصية 🚫"

    name = user.first_name if user.first_name else "مخفي 👤"
    username = f"@{user.username}" if user.username else "لا يوجد معرف 📭"
    is_bot = "نعم 🤖" if user.bot else "لا 👤"
    
    info_text = (
        "╭━━━ 🎴 **الملف الشخصي المتكامل** ━━━╮\n"
        f"👤 **الاسم الكامل:** {name}\n"
        f"🆔 **الآيدي (ID):** `{user.id}`\n"
        f"🔗 **المعرف:** {username}\n"
        f"🤖 **هل هو بوت؟** {is_bot}\n"
        f"📝 **البايو (النبذة):** {bio}\n"
        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )

    try:
        if user.photo:
            path = await client.download_profile_photo(user)
            await client.send_file(event.chat_id, path, caption=info_text)
            os.remove(path)
            return
    except Exception:
        pass
    await client.send_message(event.chat_id, info_text)


@client.on(events.NewMessage(outgoing=True, pattern=r'^/معلوماتي$'))
async def my_full_info(event):
    await event.delete()
    me = await client.get_me()
    uptime = datetime.datetime.now() - BOT_START_TIME
    text = (
        "📊 **تقرير معلومات حسابك الشخصي:**\n\n"
        f"• **الاسم:** {me.first_name}\n"
        f"• **الآيدي:** `{me.id}`\n"
        f"• **المعرف:** @{me.username}\n"
        f"• **رقم الهاتف:** +{me.phone}\n"
        f"• **مدة تشغيل اليوزر بوت:** `{str(uptime).split('.')[0]}`"
    )
    await client.send_message(event.chat_id, text)


# ==============================================================================
# القسم الرابع: التكرار الصاروخي، المقالب، والتحكم بالرسائل
# ==============================================================================

@client.on(events.NewMessage(outgoing=True, pattern=r'^/تكرار\s+(\d+)\s+(.*)$'))
async def repeat_message(event):
    await event.delete()
    count = min(int(event.pattern_match.group(1)), 1000)
    text = event.pattern_match.group(2)
    STOP_SPAM["status"] = False
    
    for _ in range(count):
        if STOP_SPAM["status"]:
            break
        try:
            await client.send_message(event.chat_id, text)
            await asyncio.sleep(0.05)
        except Exception:
            break

@client.on(events.NewMessage(outgoing=True, pattern=r'^/ايقاف_التكرار$'))
async def stop_repeat(event):
    await event.delete()
    STOP_SPAM["status"] = True
    await client.send_message(event.chat_id, "🛑 **تم إيقاف عملية التكرار بنجاح.**")


@client.on(events.NewMessage(outgoing=True, pattern=r'^/قصف$'))
async def spam_joke(event):
    await event.delete()
    jokes = [
        "يا عيال خويي ذا غريب عجيب وفيه فصلة 😂",
        "اقول تبي صامولي حار ولا فطيرة جبن؟ 🍔",
        "ياخي إنت منور الخاص عندي صراحة 🔥",
        "جالس أجرب اليوزر بوت الأسطوري الجديد عليك لا تدقق 😂",
        "يا هلا والله بالغايب الي ما يغيب 🚀"
    ]
    for j in jokes:
        await client.send_message(event.chat_id, j)
        await asyncio.sleep(0.4)


@client.on(events.NewMessage(outgoing=True, pattern=r'^/حذف\s+(\d+)$'))
async def delete_my_messages(event):
    count = int(event.pattern_match.group(1))
    await event.delete()
    deleted = 0
    async for msg in client.iter_messages(event.chat_id, from_user='me', limit=count):
        try:
            await msg.delete()
            deleted += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    temp = await client.send_message(event.chat_id, f"🗑️ **تم بنجاح حذف {deleted} من رسائلك السابقة.**")
    await asyncio.sleep(3)
    await temp.delete()


# ==============================================================================
# القسم الخامس: السرعة، الأدوات، والوقت والذكاء
# ==============================================================================

@client.on(events.NewMessage(outgoing=True, pattern=r'^(?:/سرعة|/ping)$'))
async def ping_cmd(event):
    start = datetime.datetime.now()
    event = await event.edit("⚡ **جاري قياس سرعة الاستجابة الخارقة...**")
    end = datetime.datetime.now()
    ms = (end - start).microseconds / 1000
    await event.edit(f"⚡ **سرعة استجابة السيرفر:** `{ms} ms` 🚀🔥")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/وقت$'))
async def time_cmd(event):
    now = datetime.datetime.now().strftime("%Y-%m-%d | %I:%M:%S %p")
    await event.edit(f"🕒 **التوقيت والتاريخ الحالي:**\n`{now}` ✨")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/حاسبة\s+(.*)$'))
async def calculator_cmd(event):
    await event.delete()
    expression = event.pattern_match.group(1)
    try:
        allowed_chars = "0123456789+-*/(). "
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            await client.send_message(event.chat_id, f"🧮 **العملية:** `{expression}`\n✨ **النتيجة:** `{result}`")
        else:
            await client.send_message(event.chat_id, "❌ رموز غير مسموحة في الحاسبة.")
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ خطأ في العملية الرياضية: {e}")


# ==============================================================================
# القسم السادس: التسلية، الألعاب، والحظ
# ==============================================================================

@client.on(events.NewMessage(outgoing=True, pattern=r'^/حكمة$'))
async def wisdom_cmd(event):
    await event.delete()
    wisdoms = [
        "«لا تحزن على ما فات، واجعل الغد أفضل من الأمس.» 🌟",
        "«النجاح ليس قاعاً يُحتل، بل قمة تُستحق بجهدك وصبرك.» 🦅",
        "«الوقت كالسيف إن لم تقطعه قطعك.» ⏳",
        "«من يتردد في اتخاذ القرار يفقد نصف حماسه.» 💡"
    ]
    await client.send_message(event.chat_id, f"💡 **حكمة اليوم الفخمة:**\n\n{random.choice(wisdoms)}")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/عملة$'))
async def coin_cmd(event):
    await event.delete()
    res = random.choice(["صورة 🦅", "كتابة 📖"])
    await client.send_message(event.chat_id, f"🪙 **نتيجة رمي العملة:** {res}")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/حظك$'))
async def luck_cmd(event):
    await event.delete()
    percentage = random.randint(15, 100)
    await client.send_message(event.chat_id, f"🎲 **نسبة حظك اليوم:** `{percentage}%` ✨")


# ==============================================================================
# القسم السابع: الإدارة والتحكم في المجموعات
# ==============================================================================

@client.on(events.NewMessage(outgoing=True, pattern=r'^/تثبيت$'))
async def pin_message_cmd(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply:
        return
    try:
        await client.pin_message(event.chat_id, reply)
        temp = await client.send_message(event.chat_id, "📌 **تم تثبيت الرسالة بنجاح.**")
        await asyncio.sleep(3)
        await temp.delete()
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ فشل التثبيت: تأكد من صلاحياتك المشرف. ({e})")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/فك_تثبيت$'))
async def unpin_message_cmd(event):
    await event.delete()
    try:
        await client.unpin_message(event.chat_id)
        temp = await client.send_message(event.chat_id, "🔓 **تم إزالة التثبيت بنجاح.**")
        await asyncio.sleep(3)
        await temp.delete()
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ فشل إلغاء التثبيت: {e}")


# ==============================================================================
# القسم الثامن: قائمة الأوامر الشاملة (رئيسية البوت)
# ==============================================================================

@client.on(events.NewMessage(outgoing=True, pattern=r'^/اوامر$'))
async def show_commands(event):
    text = (
        "🔥 **قائمة الأوامر الأسطورية الشاملة والضخمة** 🔥\n\n"
        "💬 **1. قسم النصوص والأزرار التفاعلية:**\n"
        "• `/زخرفة [النص]` ⟸ يفتح لك لوحة أزرار زخرفة عربية وإنجليزية فخمة.\n"
        "• `/ترجمة [النص]` ⟸ يفتح لك لوحة أزرار ترجمة فورية متعددة اللغات.\n\n"
        "🤖 **2. نظام الرد التلقائي والتكرار:**\n"
        "• `/اضافة_رد_تلقائي [النص]` ⟸ تعيين رد أوفلاين فوري.\n"
        "• `/حذف_رد_تلقائي` ⟸ إيقاف الرد الآلي.\n"
        "• `/الرد_التلقائي` ⟸ عرض الرد الحالي.\n"
        "• `/تكرار [العدد] [النص]` ⟸ تكرار صاروخي (حتى 1000).\n"
        "• `/ايقاف_التكرار` ⟸ إيقاف التكرار فوراً.\n"
        "• `/قصف` ⟸ إرسال مقالب وسيناريوهات متتالية.\n"
        "• `/حذف [العدد]` ⟸ مسح رسائلك السابقة بسرعة.\n\n"
        "👤 **3. أدوات الحسابات والمعلومات:**\n"
        "• `/id` ⟸ جلب معلومات الشخص كاملة (الصورة + البايو + الآيدي).\n"
        "• `/معلوماتي` ⟸ تقرير شامل عن حسابك.\n\n"
        "⚡ **4. السرعة والأدوات والشبكة:**\n"
        "• `/سرعة` أو `/ping` ⟸ قياس سرعة الاستجابة الخارقة.\n"
        "• `/وقت` ⟸ الوقت والتاريخ الحالي.\n"
        "• `/حاسبة [عملية]` ⟸ حسابات رياضية سريعة وسهلة.\n\n"
        "🎮 **5. التسلية والألعاب:**\n"
        "• `/حكمة` ⟸ إرسال حكمة يومية عميقة.\n"
        "• `/عملة` ⟸ رمي عملة (صورة/كتابة).\n"
        "• `/حظك` ⟸ نسبة الحظ اليومي.\n\n"
        "🛠️ **6. إدارة المجموعات:**\n"
        "• `/تثبيت` ⟸ تثبيت رسالة بالرد.\n"
        "• `/فك_تثبيت` ⟸ إزالة التثبيت.\n"
    )
    await event.edit(text)


# --- رسالة بدء التشغيل الأساسية في السيرفر ---
print("=" * 70)
print("🚀 [MEGA USERBOT v3.0] تم تحميل السيرفر والأوامر بنجاح تام!")
print("💡 حالة النظام: جاهز للعمل بكامل القوة والأزرار التفاعلية الفخمة.")
print("=" * 70)

# بدء تشغيل البوت واستمراره
client.start()
client.run_until_disconnected()
