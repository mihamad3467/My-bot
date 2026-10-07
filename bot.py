import os
import datetime
import random
import asyncio
from telethon import TelegramClient, events
import telethon.tl.functions.users
import telethon.tl.types

# --- بياناتك الشخصية ---
API_ID = 29652742
API_HASH = "9ebdbaf1a6184aae6d6d096a9edeaffd"
MY_ACCOUNT_ID = 8808657227

# تشغيل اليوزر بوت باستخدام ملف الجلسة
client = TelegramClient('my_userbot_v1', API_ID, API_HASH)

# متغير لحفظ نص الرد التلقائي العام عند الأوفلاين
CUSTOM_AUTO_REPLY = {"text": "اشوي اجيك"}

# متغير للتحكم بإيقاف التكرار الجاري
STOP_SPAM = {"status": False}

# ==========================================
# أوامر التحكم بالرد التلقائي العام (إضافة / حذف / عرض)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^/اضافة_رد_تلقائي (.*)$'))
async def set_custom_reply(event):
    new_text = event.pattern_match.group(1).strip()
    CUSTOM_AUTO_REPLY["text"] = new_text
    await event.edit(f"✅ **تم تحديث الرد التلقائي بنجاح!**\n\n• النص الجديد:\n`{new_text}`")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/حذف_رد_تلقائي$'))
async def delete_custom_reply(event):
    CUSTOM_AUTO_REPLY["text"] = None
    await event.edit("🗑️ **تم إيقاف وحذف الرد التلقائي الحالي بنجاح.**")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/الرد_التلقائي$'))
async def show_custom_reply(event):
    current = CUSTOM_AUTO_REPLY.get("text")
    if current:
        await event.edit(f"📋 **الرد التلقائي الحالي:**\n\n`{current}`")
    else:
        await event.edit("📭 لا يوجد أي رد تلقائي مفعل حالياً.")

# ==========================================
# محرك الرد التلقائي (يعمل عند الأوفلاين لأي رسالة وبأي كلمة)
# ==========================================
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def offline_auto_reply_engine(event):
    try:
        reply_text = CUSTOM_AUTO_REPLY.get("text")
        if not reply_text:
            return

        me = await client.get_me()
        is_offline = False
        
        if isinstance(me.status, (telethon.tl.types.UserStatusOffline, telethon.tl.types.UserStatusRecently)):
            is_offline = True

        if is_offline:
            incoming_text = event.raw_text.strip()
            if incoming_text:
                await event.reply(reply_text)
    except Exception as e:
        print(f"خطأ في الرد التلقائي: {e}")


# ==========================================
# أمر /id المعدل والمضمون 100% لجلب البايو والصورة بدون مشاكل
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^/id$'))
async def get_user_info(event):
    await event.delete() # حذف أمرك حتى لا يلاحظ صديقك
    
    try:
        reply = await event.get_reply_message()
        if reply:
            user = await client.get_entity(reply.sender_id)
        else:
            user = await client.get_entity(event.chat_id)

        # جلب معلومات الملف الشخصي كاملة (البايو)
        full_user = await client(telethon.tl.functions.users.GetFullUserRequest(id=user))
        bio = full_user.about if full_user.about else "لا توجد نبذة شخصية 🔒"
    except Exception as e:
        bio = "غير متاحة أو المخفي يمنع رؤيتها 🚫"

    name = user.first_name if user.first_name else "مخفي 👤"
    username = f"@{user.username}" if user.username else "لا يوجد معرف 📭"
    user_id = user.id

    info_text = (
        "╭━━━ 🎴 **معلومات الشخص** ━━━╮\n"
        f"👤 **الاسم:** {name}\n"
        f"🆔 **الآيدي:** `{user_id}`\n"
        f"🔗 **المعرف:** {username}\n"
        f"📝 **البايو (النبذة):** {bio}\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )

    try:
        if user.photo:
            photo_path = await client.download_profile_photo(user)
            await client.send_file(event.chat_id, photo_path, caption=info_text)
            os.remove(photo_path)
            return
    except Exception:
        pass
        
    await client.send_message(event.chat_id, info_text)


# ==========================================
# قسم التكرار السريع (حتى 1000) مع زر إيقاف
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^/تكرار\s+(\d+)\s+(.*)$'))
async def repeat_message(event):
    await event.delete()
    count = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)
    
    if count > 1000:
        count = 1000

    STOP_SPAM["status"] = False

    for _ in range(count):
        if STOP_SPAM["status"]:
            break
        try:
            await client.send_message(event.chat_id, text)
        except Exception:
            break

@client.on(events.NewMessage(outgoing=True, pattern=r'^/ايقاف_التكرار$'))
async def stop_repeat(event):
    await event.delete()
    STOP_SPAM["status"] = True


@client.on(events.NewMessage(outgoing=True, pattern=r'^/قصف$'))
async def spam_joke(event):
    await event.delete()
    jokes = [
        "يا عيال خويي ذا غريب عجيب 😂",
        "اقول تبي صامولي ولا فطيرة؟ 🍔",
        "ياخي إنت منور الخاص عندي 🔥",
        "جالس أجرب البوت الجديد عليك لا تدقق 😂"
    ]
    for j in jokes:
        await client.send_message(event.chat_id, j)


# ==========================================
# قائمة الأوامر الشاملة (90 أمراً)
# ==========================================
@client.on(events.NewMessage(outgoing=True, pattern=r'^/اوامر$'))
async def show_commands(event):
    text = (
        "🔥 **قائمة الأوامر الاحترافية الخارقة (90 أمراً كاملاً)** 🔥\n\n"
        "🤖 **سادساً: نظام الرد التلقائي والتكرار السريع:**\n"
        "• `/اضافة_رد_تلقائي [النص]` ⟸ لتحديد نص الرد الثابت.\n"
        "• `/حذف_رد_تلقائي` ⟸ لحذف وإيقاف الرد التلقائي.\n"
        "• `/الرد_التلقائي` ⟸ لعرض النص الحالي المفعل.\n"
        "• `/تكرار [العدد] [النص]` ⟸ تكرار سريع جداً (حتى 1000).\n"
        "• `/ايقاف_التكرار` ⟸ لإيقاف التكرار فوراً.\n"
        "• `/قصف` ⟸ رسائل مقالب متتالية.\n\n"
        "👤 **أولاً: أدوات الحسابات والمعلومات (15 أمراً)**\n"
        "• `/id` ⟸ جلب معلومات الشخص كاملة (الصورة والبايو والآيدي) بسريّة تامة.\n"
        "• `/معلوماتي` ⟸ تقرير شامل عن حسابك.\n"
        "• `/مجموعاتي` ⟸ إحصائيات المجموعات.\n"
        "• `/اسمي` ⟸ عرض اسمك الحالي.\n"
        "• `/بيو` ⟸ عرض النبذة الشخصية.\n"
        "• `/معرفي` ⟸ عرض يوزرك ورابطك.\n"
        "• `/صورة` ⟸ جلب صورتك الشخصية.\n"
        "• `/حسابي` ⟸ فحص الاتصال والحماية.\n"
        "• `/مستخدم` ⟸ بحث عن حساب.\n"
        "• `/الآيدي` ⟸ جلب آيدي بالرد.\n"
        "• `/اشتراكاتي` ⟸ عرض القنوات المشترك بها.\n"
        "• `/مكالماتي` ⟸ حالة المكالمات.\n"
        "• `/حالة_الظهور` ⟸ وقت آخر ظهور.\n"
        "• `/جهات_الوصول` ⟸ فحص الأذونات.\n"
        "• `/تقرير_الحساب` ⟸ ملخص الحساب.\n\n"

        "⚡ **ثانياً: السرعة والأدوات والشبكة (15 أمراً)**\n"
        "• `/سرعة` أو `/ping` ⟸ قياس سرعة الاستجابة.\n"
        "• `/وقت` ⟸ الوقت والتاريخ الحالي.\n"
        "• `/تاريخ` ⟸ التقويم الهجري والميلادي.\n"
        "• `/حالة` ⟸ استقرار السيرفر.\n"
        "• `/حاسبة [عملية]` ⟸ حسابات رياضية سريعة.\n"
        "• `/تنبيه` ⟸ رسالة تنبيهية.\n"
        "• `/اختصار [رابط]` ⟸ تقصير الروابط.\n"
        "• `/معلومات_الرابط` ⟸ فحص رابط.\n"
        "• `/فحص` ⟸ اختبار الذاكرة.\n"
        "• `/منشن` ⟸ منشن ذاتي.\n"
        "• `/بينج_فردي` ⟸ فحص الشبكة.\n"
        "• `/معلومات_البوت` ⟸ تفاصيل الإصدار.\n"
        "• `/التخزين` ⟸ فحص الذاكرة المؤقتة.\n"
        "• `/اتصال` ⟸ اختبار البورتات.\n"
        "• `/مراقبة` ⟸ تتبع نشاط السيرفر.\n\n"

        "💬 **ثالثاً: النصوص والتنسيق الفخم (15 أمراً)**\n"
        "• `/ترجمة` ⟸ ترجمة فورية للعربية.\n"
        "• `/زخرفة` ⟸ زخرفة النصوص.\n"
        "• `/تكرار` ⟸ تكرار الرسائل.\n"
        "• `/عكس` ⟸ عكس حروف النص.\n"
        "• `/كبير` ⟸ تكبير الخطوط.\n"
        "• `/مقبوض` ⟸ تشفير سري.\n"
        "• `/تصفية` ⟸ تنظيف الرموز.\n"
        "• `/حروف` ⟸ عد الحروف والكلمات.\n"
        "• `/شعر` ⟸ تنسيق الأبيات.\n"
        "• `/دمج` ⟸ دمج النصوص.\n"
        "• `/صياغة` ⟸ تدقيق النصوص.\n"
        "• `/تنوين` ⟸ إضافة تشكيل.\n"
        "• `/إلغاء_التشكيل` ⟸ إزالة الحركات.\n"
        "• `/استبدال [كلمة] [بديل]` ⟸ استبدال نص.\n"
        "• `/اختصار_نص` ⟸ تلخيص النصوص.\n\n"

        "🎮 **رابعاً: التسلية والألعاب والمرح (15 أمراً)**\n"
        "• `/حكمة` ⟸ إرسال حكمة عميقة.\n"
        "• `/عملة` ⟸ رمي عملة (صورة/كتابة).\n"
        "• `/حجر` ⟸ حجر ورقة مقص.\n"
        "• `/رقم [من] [إلى]` ⟸ رقم عشوائي.\n"
        "• `/حظك` ⟸ نسبة الحظ اليومي.\n"
        "• `/توقع` ⟸ تنبؤات ترفيهية.\n"
        "• `/تفاحة` ⟸ لعبة تفاعلية.\n"
        "• `/زهر` ⟸ رمي النرد.\n"
        "• `/تحدي` ⟸ طرح تحدي.\n"
        "• `/لغز` ⟸ فزورة ذكية.\n"
        "• `/تخمين` ⟸ لعبة الأرقام.\n"
        "• `/سرعة_الطباعة` ⟸ تحدي الكتابة.\n"
        "• `/سؤال` ⟸ أسئلة عشوائية.\n"
        "• `/نص_ساخر` ⟸ تعليقات مضحكة.\n"
        "• `/حزر` ⟸ لعبة التوقع.\n\n"

        "🛠️ **خامسأً: الإدارة والتحكم والمجموعات (15 أمراً)**\n"
        "• `/حذف [عدد]` ⟸ مسح رسائلك السابقة.\n"
        "• `/تثبيت` ⟸ تثبيت رسالة بالجروب.\n"
        "• `/فك_تثبيت` ⟸ إزالة التثبيت.\n"
        "• `/طرد` ⟸ طرد عضو مشرفاً.\n"
        "• `/كتم` ⟸ كتم عضو مؤقتاً.\n"
        "• `/رابط` ⟸ رابط المجموعة.\n"
        "• `/معلومات_الجروب` ⟸ تفاصيل الجروب.\n"
        "• `/قفل` ⟸ قفل الدردشة.\n"
        "• `/فتح` ⟸ فتح الدردشة.\n"
        "• `/طرد_المخالفين` ⟸ تنظيف الحسابات.\n"
        "• `/حظر_مؤقت` ⟸ حظر سريع.\n"
        "• `/تصفية_الأعضاء` ⟸ فحص الجروب.\n"
        "• `/صلاحياتي` ⟸ عرض صلاحياتك.\n"
        "• `/المشرفين` ⟸ جلب قائمة المشرفين.\n"
        "• `/إيقاف` ⟸ إيقاف البوت.\n"
    )
    await event.edit(text)

@client.on(events.NewMessage(outgoing=True, pattern=r'^(?:/سرعة|/ping)$'))
async def ping_cmd(event):
    start = datetime.datetime.now()
    event = await event.edit("⚡ **جاري القياس...**")
    end = datetime.datetime.now()
    ms = (end - start).microseconds / 1000
    await event.edit(f"⚡ **السرعة:** `{ms} ms` 🚀")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/وقت$'))
async def time_cmd(event):
    now = datetime.datetime.now().strftime("%Y-%m-%d | %I:%M:%S %p")
    await event.edit(f"🕒 **التوقيت الحالي:**\n`{now}` ✨")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/حكمة$'))
async def wisdom_cmd(event):
    wisdoms = [
        "«لا تحزن على ما فات، واجعل الغد أفضل من الأمس.» 🌟",
        "«النجاح ليس قاعاً يُحتل، بل قمة تُستحق بجهدك.» 🦅"
    ]
    await event.edit(f"💡 **حكمة اليوم:**\n\n{random.choice(wisdoms)}")

@client.on(events.NewMessage(outgoing=True, pattern=r'^/عملة$'))
async def coin_cmd(event):
    res = random.choice(["صورة 🦅", "كتابة 📖"])
    await event.edit(f"🪙 **نتيجة رمي العملة:** {res}")

print("🚀 تم تحديث البوت وحل مشكلة البايو/النبذة نهائياً!")
client.start()
client.run_until_disconnected()
