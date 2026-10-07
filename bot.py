import os
from telethon import TelegramClient, events
import telethon.tl.functions.users
import telethon.tl.types

# --- بياناتك الشخصية ---
API_ID = 29652742
API_HASH = "9ebdbaf1a6184aae6d6d096a9edeaffd"
MY_ACCOUNT_ID = 8808657227  # آيدي حسابك

# تشغيل اليوزر بوت على حسابك الشخصي
client = TelegramClient('my_userbot_v1', API_ID, API_HASH)

# ==========================================
# الأوامر الأساسية للنسخة 1.0
# ==========================================

# 1. أمر /اوامر
@client.on(events.NewMessage(outgoing=True, pattern=r'^/اوامر$'))
async def show_commands(event):
    commands_text = (
        "⚡ **قائمة أوامر اليوزر بوت (النسخة 1.0):**\n\n"
        "👤 **أدوات الحسابات:**\n"
        "• `/id` - جلب معلومات تفصيلية عن الشخص (بالرد على رسالته أو في خاصه) مع الصورة والنبذة.\n\n"
        "⚡ **التفاعل والسرعة:**\n"
        "• `/سرعة` - فحص استجابة وسرعة البوت.\n"
        "• `/وقت` - عرض الوقت الحالي.\n\n"
        "⚙️ **الحالة:**\n"
        "• `/معلوماتي` - عرض معلومات حسابك الأساسية.\n"
    )
    await event.edit(commands_text)

# 2. أمر /id المفصل (يجلب الآيدي، الاسم، اليوزر، النبذة، والصورة الشخصية)
@client.on(events.NewMessage(outgoing=True, pattern=r'^/id$'))
async def get_user_info(event):
    reply = await event.get_reply_message()
    if reply:
        user = await client.get_entity(reply.sender_id)
    else:
        user = await client.get_entity(event.chat_id)

    # جلب النبذة الشخصية (Bio)
    try:
        full_user = await client(
            telethon.tl.functions.users.GetFullUserRequest(id=user.id)
        )
        bio = full_user.about if full_user.about else "لا توجد نبذة شخصية."
    except Exception:
        bio = "غير قادر على جلب النبذة."

    name = user.first_name if user.first_name else "مخفي"
    username = f"@{user.username}" if user.username else "لا يوجد يوزر"
    user_id = user.id

    info_text = (
        "👤 **معلومات الشخص:**\n\n"
        f"• **الاسم:** {name}\n"
        f"• **الآيدي (ID):** `{user_id}`\n"
        f"• **المعرف (Username):** {username}\n"
        f"• **النبذة (Bio):** {bio}"
    )

    # إرسال الصورة الشخصية مع النص إن وجدت
    if user.photo:
        photo_path = await client.download_profile_photo(user)
        await client.send_file(event.chat_id, photo_path, caption=info_text)
        os.remove(photo_path)
        await event.delete()
    else:
        await event.edit(info_text)

# 3. أمر /سرعة
@client.on(events.NewMessage(outgoing=True, pattern=r'^/سرعة$'))
async def ping_cmd(event):
    await event.edit("⚡ البوت يعمل بكفاءة عالية على حسابك!")

# 4. أمر /وقت
@client.on(events.NewMessage(outgoing=True, pattern=r'^/وقت$'))
async def time_cmd(event):
    import datetime
    current_time = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S")
    await event.edit(f"🕒 **الوقت الحالي:** `{current_time}`")

# 5. أمر /معلوماتي
@client.on(events.NewMessage(outgoing=True, pattern=r'^/معلوماتي$'))
async def my_info(event):
    me = await client.get_me()
    await event.edit(
        f"👑 **معلومات حسابك الأساسية:**\n\n"
        f"• الاسم: {me.first_name}\n"
        f"• الآيدي: `{me.id}`\n"
        f"• اليوزر: @{me.username if me.username else 'لا يوجد'}"
    )

print("🚀 جاري تشغيل النسخة الأولى 1.0 من اليوزر بوت...")
client.start()
client.run_until_disconnected()
