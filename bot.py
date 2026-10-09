# ==============================================================================
# 🌟 المشروع الأسطوري: اليوزر بوت الفخم والضخم (Mega Userbot Pro v4.3 - Cloner Fixed)
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

# --- إعدادات الحساب الأساسية ---
API_ID = 29652742
API_HASH = "9ebdbaf1a6184aae6d6d096a9edeaffd"

# 🟢 قائمة الآيديات المسموح لها باستخدام الأوامر (أنت + صديقك)
ALLOWED_USERS = [8808657227, 8488628167]

# استخدام ملف الجلسة المحلي الموجود في المستودع مباشرة لضمان العمل المستقر
client = TelegramClient('my_userbot_v1', API_ID, API_HASH)

# --- الهياكل ومتغيرات الحالة العامة ---
CUSTOM_AUTO_REPLY = {"text": None}
STOP_SPAM = {"status": False}
AFK_MODE = {"status": False, "reason": "غير متواجد حالياً 🔒"}
BOT_START_TIME = datetime.datetime.now()

# متغيرات لحفظ النسخة الأصلية قبل عملية /نسخ (لاستعادتها عند /الغاء_نسخ)
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
# القسم الأول: نظام الرد التلقائي والـ AFK
# ==============================================================================

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text.startswith('/اضافة_رد_تلقائي')))
async def set_custom_reply(event):
    await event.delete()
    new_text = event.raw_text.replace('/اضافة_رد_تلقائي', '').strip()
    CUSTOM_AUTO_REPLY["text"] = new_text
    await client.send_message(event.chat_id, f"✅ **تم تفعيل الرد التلقائي:**\n`{new_text}`")

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/حذف_رد_تلقائي'))
async def delete_custom_reply(event):
    await event.delete()
    CUSTOM_AUTO_REPLY["text"] = None
    await client.send_message(event.chat_id, "🗑️ **تم مسح الرد التلقائي.**")

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text.startswith('/afk')))
async def set_afk_mode(event):
    await event.delete()
    reason = event.raw_text.replace('/afk', '').strip()
    if reason:
        AFK_MODE["reason"] = reason
    AFK_MODE["status"] = True
    await client.send_message(event.chat_id, f"💤 **تم تفعيل وضع AFK:**\n📌 **السبب:** `{AFK_MODE['reason']}`")

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/الغاء_afk'))
async def disable_afk_mode(event):
    await event.delete()
    AFK_MODE["status"] = False
    await client.send_message(event.chat_id, f"⚡ **تم إلغاء وضع AFK وعودتك للنشاط.**")


# ==============================================================================
# القسم الثاني: نظام نسخ الحسابات الخرافي المؤكد (/نسخ و /الغاء_نسخ)
# ==============================================================================

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/نسخ'))
async def clone_user_profile(event):
    await event.delete()
    reply = await event.get_reply_message()
    if not reply:
        await client.send_message(event.chat_id, "⚠️ **يجب الرد على رسالة الشخص المراد نسخ حسابه لاستخدام هذا الأمر!**")
        return
    
    try:
        target_user = await client.get_entity(reply.sender_id)
        full_target = await client(telethon.tl.functions.users.GetFullUserRequest(id=target_user))
        
        # استخراج البايو بشكل سليم ومضبوط حسب تحديثات تليجرام الأخيرة
        target_bio = ""
        if hasattr(full_target, 'full_user') and hasattr(full_target.full_user, 'about'):
            target_bio = full_target.full_user.about or ""
        elif hasattr(full_target, 'about'):
            target_bio = full_target.about or ""

        # حفظ بياناتنا الأصلية أولاً إذا لم تكن محفوظة
        me = await client.get_me()
        if not ORIGINAL_PROFILE["first_name"]:
            ORIGINAL_PROFILE["first_name"] = me.first_name
            # جلب بايو حسابنا الحالي لحفظه
            try:
                my_full = await client(telethon.tl.functions.users.GetFullUserRequest(id='me'))
                ORIGINAL_PROFILE["about"] = my_full.full_user.about if hasattr(my_full, 'full_user') else ""
            except:
                ORIGINAL_PROFILE["about"] = ""
        
        # 1. نسخ الاسم
        new_name = target_user.first_name if target_user.first_name else "مستخدم"
        await client(telethon.tl.functions.account.UpdateProfileRequest(first_name=new_name))
        
        # 2. نسخ البايو (النبذة)
        if target_bio:
            await client(telethon.tl.functions.account.UpdateProfileRequest(about=target_bio))
        
        # 3. نسخ الصورة الشخصية إن وجدت
        photo_msg = "ولكن لم يتم العثور على صورة شخصية."
        if target_user.photo:
            path = await client.download_profile_photo(target_user)
            file = await client.upload_file(path)
            await client(telethon.tl.functions.photos.UploadProfilePhotoRequest(file=file))
            os.remove(path)
            photo_msg = "وتم نسخ الصورة الشخصية بنجاح 🖼️"

        await client.send_message(
            event.chat_id, 
            f"🔥 **تم نسخ حساب الشخص بنجاح!**\n\n👤 **الاسم:** {new_name}\n📝 **البايو:** `{target_bio if target_bio else 'لا توجد نبذة'}`\n{photo_msg}\n\nلإعادة حسابك كما كان، اكتب: `/الغاء_نسخ`"
        )
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ حدث خطأ أثناء النسخ: {e}")

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/الغاء_نسخ'))
async def restore_user_profile(event):
    await event.delete()
    if not ORIGINAL_PROFILE["first_name"]:
        await client.send_message(event.chat_id, "⚠️ ليس هناك أي عملية نسخ مسجلة حالياً لكي يتم إرجاعها.")
        return
    try:
        # استعادة الاسم والبايو الأصليين
        await client(telethon.tl.functions.account.UpdateProfileRequest(
            first_name=ORIGINAL_PROFILE["first_name"],
            about=ORIGINAL_PROFILE["about"] if ORIGINAL_PROFILE["about"] else ""
        ))
        
        # حذف الصور الشخصية المضافة للرجوع للصورة الأساسية
        photos = await client.get_profile_photos('me')
        if photos:
            await client(telethon.tl.functions.photos.DeletePhotosRequest(id=[photos[0]]))

        await client.send_message(event.chat_id, "⚡ **تم إلغاء النسخ واستعادة معلومات حسابك الأصلي بنجاح!**")
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ حدث خطأ أثناء الاستعادة: {e}")


# ==============================================================================
# القسم الثالث: الزخرفة والترجمة الفورية (إنجليزية)
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
            await client.send_message(event.chat_id, "⚠️ اكتب النص بعد الأمر أو رد على رسالة لزخرفتها!")
            return

    dec_res = (
        "✨ **قائمة الزخارف الاحترافية:**\n\n"
        f"🌟 **إنجليزي 1:** `{ENGLISH_DECORATIONS['1'](text)}`\n"
        f"💎 **إنجليزي 2:** `{ENGLISH_DECORATIONS['2'](text)}`\n"
        f"🔥 **عربي 1:** `{ARABIC_DECORATIONS['1'](text)}`\n"
        f"⭐ **عربي 2:** `{ARABIC_DECORATIONS['4'](text)}`"
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
            await client.send_message(event.chat_id, "⚠️ رد على رسالة بـ `/ترجمة` أو اكتب النص بعدها لترجمته للإنجليزية!")
            return
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        await client.send_message(event.chat_id, f"🌐 **الترجمة إلى الإنجليزية:**\n\n`{translated}`")
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ خطأ في الترجمة: {e}")


# ==============================================================================
# القسم الرابع: أدوات الحسابات والمعلومات الفخمة (/id المضبوط)
# ==============================================================================

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and (e.raw_text == '/id' or e.raw_text.startswith('/id'))))
async def get_user_info_fixed(event):
    await event.delete()
    try:
        reply = await event.get_reply_message()
        if reply:
            user = await client.get_entity(reply.sender_id)
        else:
            user = await client.get_entity(event.chat_id)

        # جلب البايو والبيانات الكاملة بشكل آمن ومتوافق تماماً
        bio = "لا توجد نبذة شخصية (Bio) 🔒"
        try:
            full_user = await client(telethon.tl.functions.users.GetFullUserRequest(id=user))
            if hasattr(full_user, 'full_user') and hasattr(full_user.full_user, 'about'):
                bio = full_user.full_user.about or bio
            elif hasattr(full_user, 'about'):
                bio = full_user.about or bio
        except Exception:
            pass

        name = user.first_name if user.first_name else "مخفي 👤"
        username = f"@{user.username}" if user.username else "لا يوجد معرف 📭"
        is_bot = "نعم 🤖" if user.bot else "لا 👤"
        
        info_text = (
            "╭━━━ 🎴 **الملف الشخصي المتكامل** ━━━╮\n"
            f"👤 **الاسم:** {name}\n"
            f"🆔 **الآيدي (ID):** `{user.id}`\n"
            f"🔗 **المعرف:** {username}\n"
            f"🤖 **هل هو بوت؟** {is_bot}\n"
            f"📝 **البايو:** {bio}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
        )

        if user.photo:
            path = await client.download_profile_photo(user)
            await client.send_file(event.chat_id, path, caption=info_text)
            os.remove(path)
            return
        
        await client.send_message(event.chat_id, info_text)
    except Exception as e:
        await client.send_message(event.chat_id, f"❌ عذراً، لم أتمكن من جلب معلومات هذا الحساب: {e}")


# ==============================================================================
# القسم الخامس: التكرار، المقالب، الحذف، والسرعة
# ==============================================================================

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text.startswith('/تكرار')))
async def repeat_message(event):
    await event.delete()
    parts = event.raw_text.split(maxsplit=2)
    if len(parts) < 3:
        return
    count = min(int(parts[1]), 500)
    text = parts[2]
    STOP_SPAM["status"] = False
    
    for _ in range(count):
        if STOP_SPAM["status"]:
            break
        try:
            await client.send_message(event.chat_id, text)
            await asyncio.sleep(0.04)
        except Exception:
            break

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/ايقاف_التكرار'))
async def stop_repeat(event):
    await event.delete()
    STOP_SPAM["status"] = True
    await client.send_message(event.chat_id, "🛑 **تم إيقاف التكرار بنجاح.**")

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text in ['/سرعة', '/ping']))
async def ping_cmd(event):
    start = datetime.datetime.now()
    msg = await client.send_message(event.chat_id, "⚡ **جاري قياس السرعة...**")
    end = datetime.datetime.now()
    ms = (end - start).microseconds / 1000
    await msg.edit(f"⚡ **سرعة استجابة السيرفر:** `{ms} ms` 🚀")

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/وقت'))
async def time_cmd(event):
    await event.delete()
    now = datetime.datetime.now().strftime("%Y-%m-%d | %I:%M:%S %p")
    await client.send_message(event.chat_id, f"🕒 **التوقيت والتاريخ الحالي:**\n`{now}` ✨")


# ==============================================================================
# القسم السادس: قائمة الأوامر الشاملة
# ==============================================================================

@client.on(events.NewMessage(func=lambda e: is_allowed(e) and e.raw_text == '/اوامر'))
async def show_commands(event):
    await event.delete()
    text = (
        "🔥 **قائمة الأوامر المحدثة والأسطورية v4.3** 🔥\n\n"
        "🎭 **1. قسم انتحال ونسخ الحسابات:**\n"
        "• `/نسخ` (بالرد على رسالة شخص) ⟸ لنسخ اسمه وبايوه وصورته بحسابك.\n"
        "• `/الغاء_نسخ` ⟸ لاستعادة اسمك وصورتك وبايوك الأصلي.\n\n"
        "✨ **2. قسم النصوص والترجمة:**\n"
        "• `/زخرفة [النص]` أو بالرد ⟸ زخرفة فورية فخمة.\n"
        "• `/ترجمة [النص]` أو بالرد ⟸ ترجمة فورية إلى الإنجليزية.\n\n"
        "👤 **3. قسم المعلومات الشخصية:**\n"
        "• `/id` أو بالرد ⟸ جلب معلومات الشخص كاملة (الاسم، الآيدي، اليوزر، البايو، والصورة).\n"
        "• `/معلوماتي` ⟸ معلومات حسابك الحالي.\n\n"
        "🚀 **4. الأدوات والتحكم:**\n"
        "• `/تكرار [العدد] [النص]` ⟸ تكرار رسائل صاروخي.\n"
        "• `/ايقاف_التكرار` ⟸ إيقاف التكرار فوراً.\n"
        "• `/سرعة` أو `/ping` ⟸ قياس سرعة السيرفر.\n"
        "• `/وقت` ⟸ عرض الوقت والتاريخ.\n"
        "• `/afk [السبب]` ⟸ وضع الغياب التلقائي.\n"
        "• `/الغاء_afk` ⟸ العودة للنشاط.\n"
    )
    await client.send_message(event.chat_id, text)


# --- رسالة التشغيل ---
print("=" * 70)
print("🚀 [MEGA USERBOT v4.3 Cloner Fixed] تم تحميل الكود بنجاح تام!")
print("=" * 70)

client.start()
client.run_until_disconnected()
