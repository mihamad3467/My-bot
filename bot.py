# ==============================================================================
# 🌟 المشروع الأسطوري: اليوزر بوت الفخم والضخم (Mega Userbot Pro v4.4 - AI Agent)
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
import telethon.tl.functions.account
from deep_translator import GoogleTranslator
import google.generativeai as genai

# --- إعدادات الحساب الأساسية والذكاء الاصطناعي ---
API_ID = 29652742
API_HASH = "9ebdbaf1a6184aae6d6d096a9edeaffd"

# 🔑 تم تركيب مفتاح Gemini API الخاص بك بنجاح
GEMINI_API_KEY = "AQ.Ab8RN6LDVdzfTMT89oU14HL7gnUayvWEtoYI3uhk02poijh2jw"
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    ai_model = None

# 🟢 قائمة الآيديات المسموح لها باستخدام الأوامر (أنت + صديقك)
ALLOWED_USERS = [8808657227, 8488628167]

# استخدام ملف الجلسة المحلي الموجود في المستودع مباشرة لضمان العمل المستقر
client = TelegramClient('my_userbot_v1', API_ID, API_HASH)

# --- الهياكل ومتغيرات الحالة العامة ---
CUSTOM_AUTO_REPLY = {"text": None}
STOP_SPAM = {"status": False}
AFK_MODE = {"status": False, "reason": "غير متواجد حالياً 🔒"}
AI_AGENT_MODE = {"status": False}  # حالة تشغيل أو إيقاف الذكاء الاصطناعي للرد على الناس
BOT_START_TIME = datetime.datetime.now()

ORIGINAL_PROFILE = {"first_name": None, "about": None}

def is_allowed(event):
    return event.sender_id in ALLOWED_USERS

# قاموس الزخارف الفخمة
ARABIC_DECORATIONS = {
    "1": lambda t: f"『 {t} 』",
    "2": lambda t: f"★[ {t} ]★",
    "3": lambda t: f"卍 {t} 卍",
    "4": lambda t: f"✨ ⦋ {t} ⦃ 🌟 ⦄ ⦊ ✨"
}

ENGLISH_DECORATIONS = {
    "1": lambda t: "".join(chr(ord(c) + 119735) if 'a' <= c <= 'z' else (chr(ord(c) + 119729) if 'A' <= c <= 'Z' else c) for c in t),
    "2": lambda t: f"𝒯:: {t} ::𝒯",
    "3": lambda t: f"🔥 ⦋ {t} ⦌ 🔥"
}


# ==============================================================================
# القسم الأول: نظام الذكاء الاصطناعي التفاعلي والتحكم (تشغيل / إيقاف / مراسلة)
# ==============================================================================

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/تشغيل_ذكاء'))
async def enable_ai(event):
    await event.delete()
    AI_AGENT_MODE["status"] = True
    await client.send_message(event.chat_id, "🤖 **تم تفعيل مساعد الذكاء الاصطناعي بنجاح!**\nسيبدأ الرد على الرسائل الواردة بشكل طبيعي وذكي.")

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/ايقاف_ذكاء'))
async def disable_ai(event):
    await event.delete()
    AI_AGENT_MODE["status"] = False
    await client.send_message(event.chat_id, "🛑 **تم إيقاف مساعد الذكاء الاصطناعي.**")

# أمر لمراسلة شخص غير مضاف لديك: /ارسل [@Username أو ID] [الرسالة]
@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text.startswith('/ارسل')))
async def send_to_stranger(event):
    await event.delete()
    parts = event.raw_text.split(maxsplit=2)
    if len(parts) < 3:
        await client.send_message(event.chat_id, "⚠️ **الصيغة الصحيحة:**\n`/ارسل @المعرف أو الآيدي النص`")
        return
    
    target = parts[1]
    message_text = parts[2]
    
    try:
        if target.isdigit():
            target_entity = int(target)
        else:
            target_entity = target

        await client.send_message(target_entity, message_text)
        await client.send_message(event.chat_id, f"✅ **تم إرسال الرسالة بنجاح إلى:** `{target}`")
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ فشل إرسال الرسالة: تأكد من صحة المعرف ({e})")

# معالج الرسائل الواردة بالخاص وردود الذكاء الاصطناعي التلقائية
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def ai_incoming_handler(event):
    try:
        if AFK_MODE["status"]:
            await event.reply(f"💤 **عذراً، صاحب الحساب غائب حالياً.**\n📌 **السبب:** `{AFK_MODE['reason']}`")
            return

        if AI_AGENT_MODE["status"] and event.raw_text.strip():
            if ai_model:
                prompt = f"أنت مساعد ذكي تتحدث نيابة عن صاحب الحساب بأسلوب طبيعي، ودي، وذكاء عالي باللغة العربية. رد على هذه الرسالة: {event.raw_text}"
                response = ai_model.generate_content(prompt)
                ai_reply = response.text if response and response.text else "أهلاً بك، وصلني ردك وسأرد عليك لاحقاً."
                await event.reply(ai_reply)
            else:
                await event.reply("⚠️ تنبيه: خطأ في إعدادات نموذج الذكاء الاصطناعي.")
    except Exception as e:
        print(f"AI Error: {e}")


# ==============================================================================
# القسم الثاني: نظام نسخ الحسابات (/نسخ و /الغاء_نسخ)
# ==============================================================================

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/نسخ'))
async def clone_user_profile(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply:
        await client.send_message(event.chat_id, "⚠️ **يجب الرد على رسالة الشخص المراد نسخ حسابه!**")
        return
    
    try:
        target_user = await client.get_entity(reply.sender_id)
        full_target = await client(telethon.tl.functions.users.GetFullUserRequest(id=target_user))
        
        target_bio = ""
        if hasattr(full_target, 'full_user') and hasattr(full_target.full_user, 'about'):
            target_bio = full_target.full_user.about or ""
        elif hasattr(full_target, 'about'):
            target_bio = full_target.about or ""

        me = await client.get_me()
        if not ORIGINAL_PROFILE["first_name"]:
            ORIGINAL_PROFILE["first_name"] = me.first_name
            try:
                my_full = await client(telethon.tl.functions.users.GetFullUserRequest(id='me'))
                ORIGINAL_PROFILE["about"] = my_full.full_user.about if hasattr(my_full, 'full_user') else ""
            except:
                ORIGINAL_PROFILE["about"] = ""
        
        new_name = target_user.first_name if target_user.first_name else "مستخدم"
        await client(telethon.tl.functions.account.UpdateProfileRequest(first_name=new_name))
        
        if target_bio:
            await client(telethon.tl.functions.account.UpdateProfileRequest(about=target_bio))
        
        photo_msg = "ولكن لم يتم العثور على صورة شخصية."
        if target_user.photo:
            path = await client.download_profile_photo(target_user)
            file = await client.upload_file(path)
            await client(telethon.tl.functions.photos.UploadProfilePhotoRequest(file=file))
            os.remove(path)
            photo_msg = "وتم نسخ الصورة الشخصية بنجاح 🖼️"

        await client.send_message(event.chat_id, f"🔥 **تم نسخ حساب الشخص بنجاح!**\n\n👤 **الاسم:** {new_name}\n📝 **البايو:** `{target_bio}`\n{photo_msg}")
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ حدث خطأ أثناء النسخ: {e}")

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/الغاء_نسخ'))
async def restore_user_profile(event):
    await event.delete()
    if not ORIGINAL_PROFILE["first_name"]:
        await client.send_message(event.chat_id, "⚠️ ليس هناك أي عملية نسخ مسجلة.")
        return
    try:
        await client(telethon.tl.functions.account.UpdateProfileRequest(
            first_name=ORIGINAL_PROFILE["first_name"],
            about=ORIGINAL_PROFILE["about"] if ORIGINAL_PROFILE["about"] else ""
        ))
        photos = await client.get_profile_photos('me')
        if photos:
            await client(telethon.tl.functions.photos.DeletePhotosRequest(id=[photos[0]]))
        await client.send_message(event.chat_id, "⚡ **تم استعادة حسابك الأصلي بنجاح!**")
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ خطأ: {e}")


# ==============================================================================
# القسم الثالث: الزخرفة، الترجمة، ومعلومات الحساب
# ==============================================================================

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text.startswith('/زخرفة')))
async def decorate_cmd(event):
    await event.delete()
    text = event.raw_text.replace('/زخرفة', '').strip()
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text
        else:
            await client.send_message(event.chat_id, "⚠️ اكتب النص أو رد على رسالة!")
            return

    dec_res = (
        "✨ **قائمة الزخارف الاحترافية:**\n\n"
        f"🌟 **إنجليزي:** `{ENGLISH_DECORATIONS['1'](text)}`\n"
        f"🔥 **عربي:** `{ARABIC_DECORATIONS['1'](text)}`"
    )
    await client.send_message(event.chat_id, dec_res)

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text.startswith('/ترجمة')))
async def translate_to_english_cmd(event):
    await event.delete()
    text = event.raw_text.replace('/ترجمة', '').strip()
    if not text:
        reply = await event.get_reply_message()
        if reply and reply.text:
            text = reply.text
        else:
            await client.send_message(event.chat_id, "⚠️ اكتب النص أو رد على رسالة!")
            return
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        await client.send_message(event.chat_id, f"🌐 **الترجمة الإنجليزية:**\n`{translated}`")
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ خطأ: {e}")

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and (e.raw_text == '/id' or e.raw_text.startswith('/id'))))
async def get_user_info_fixed(event):
    await event.delete()
    try:
        reply = await event.get_reply_message()
        user = await client.get_entity(reply.sender_id) if reply else await client.get_entity(event.chat_id)
        
        bio = "لا توجد نبذة شخصية 🔒"
        try:
            full_user = await client(telethon.tl.functions.users.GetFullUserRequest(id=user))
            if hasattr(full_user, 'full_user') and hasattr(full_user.full_user, 'about'):
                bio = full_user.full_user.about or bio
        except:
            pass

        info_text = (
            "╭━━━ 🎴 **الملف الشخصي** ━━━╮\n"
            f"👤 **الاسم:** {user.first_name}\n"
            f"🆔 **الآيدي:** `{user.id}`\n"
            f"🔗 **المعرف:** @{user.username if user.username else 'لا يوجد'}\n"
            f"📝 **البايو:** {bio}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        if user.photo:
            path = await client.download_profile_photo(user)
            await client.send_file(event.chat_id, path, caption=info_text)
            os.remove(path)
            return
        await client.send_message(event.chat_id, info_text)
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ خطأ: {e}")


# ==============================================================================
# القسم الرابع: قائمة الأوامر الشاملة
# ==============================================================================

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/اوامر'))
async def show_commands(event):
    await event.delete()
    text = (
        "🔥 **قائمة الأوامر الذكية v4.4** 🔥\n\n"
        "🤖 **1. قسم الذكاء الاصطناعي:**\n"
        "• `/تشغيل_ذكاء` ⟸ تفعيل ردود AI التلقائية على الناس.\n"
        "• `/ايقاف_ذكاء` ⟸ إيقاف ردود AI.\n"
        "• `/ارسل [@المعرف] [النص]` ⟸ مراسلة أي شخص غير مضاف.\n\n"
        "🎭 **2. النسخ والتحكم:**\n"
        "• `/نسخ` (بالرد) ⟸ انتحال حساب الشخص.\n"
        "• `/الغاء_نسخ` ⟸ استعادة حسابك.\n\n"
        "✨ **3. الخدمات:**\n"
        "• `/زخرفة [النص]` | `/ترجمة [النص]` | `/id`\n"
    )
    await client.send_message(event.chat_id, text)


# --- التشغيل ---
print("=" * 70)
print("🚀 [MEGA USERBOT v4.4 AI Agent] تم تحميل البوت بنجاح تام!")
print("=" * 70)

client.start()
client.run_until_disconnected()
