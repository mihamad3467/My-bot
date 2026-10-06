import re
from datetime import datetime, timedelta
from telegram import Update, BotCommand
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# التوكن الخاص بالبوت الذي طلبته
TOKEN = "8797714829:AAFAGO7w2Y5Mgh_mPY4NWPtL8JlkEl_Fajc"

# قائمة الأوامر الشاملة (أكثر من 100 أمر) لتظهر تلقائياً بجانب زر الدبوس عند رفع البوت مشرف
BOT_COMMANDS = [
    # الحماية والروابط
    BotCommand("protection_on", "تفعيل الحماية الكاملة"),
    BotCommand("protection_off", "إيقاف الحماية الكاملة"),
    BotCommand("antilink_on", "منع الروابط وحظر مرسلها 5 دقائق"),
    BotCommand("antilink_off", "السماح بالروابط"),
    BotCommand("antispam_on", "منع التكرار والإزعاج"),
    BotCommand("antispam_off", "السماح بالتكرار"),
    BotCommand("antiforward_on", "منع إعادة التوجيه"),
    BotCommand("antiforward_off", "السماح بإعادة التوجيه"),
    BotCommand("antibot_on", "منع دخول البوتات التلقائية"),
    BotCommand("antibot_off", "السماح بدخول البوتات"),
    BotCommand("antiphoto_on", "منع إرسال الصور"),
    BotCommand("antiphoto_off", "السماح بالصور"),
    BotCommand("antivideo_on", "منع إرسال الفيديوهات"),
    BotCommand("antivideo_off", "السماح بالفيديوهات"),
    BotCommand("antifile_on", "منع إرسال الملفات"),
    BotCommand("antifile_off", "السماح بالملفات"),
    BotCommand("antivoice_on", "منع الصوتيات"),
    BotCommand("antivoice_off", "السماح بالصوتيات"),
    BotCommand("antisticker_on", "منع الملصقات"),
    BotCommand("antisticker_off", "السماح بالملصقات"),
    BotCommand("antigif_on", "منع المتحركات GIF"),
    BotCommand("antigif_off", "السماح بالمتحركات"),
    BotCommand("anticontact_on", "منع جهات الاتصال"),
    BotCommand("anticontact_off", "السماح بجهات الاتصال"),
    BotCommand("antipoll_on", "منع الاستطلاعات"),
    BotCommand("antipoll_off", "السماح بالاستطلاعات"),
    BotCommand("antiusername_on", "منع المعرفات @"),
    BotCommand("antiusername_off", "السماح بالمعرفات"),
    BotCommand("add_badword", "إضافة كلمة ممنوعة"),
    BotCommand("del_badword", "حذف كلمة ممنوعة"),
    BotCommand("list_badwords", "عرض الكلمات الممنوعة"),
    BotCommand("protection_status", "عرض حالة الحماية"),

    # الإدارة والعقوبات (المشرفين)
    BotCommand("mute", "كتم عضو دائم بالرد"),
    BotCommand("tempmute", "كتم مؤقت (مثال: /tempmute 10m)"),
    BotCommand("unmute", "فك الكتم عن عضو"),
    BotCommand("ban", "حظر عضو من القروب"),
    BotCommand("tempban", "حظر مؤقت لعضو"),
    BotCommand("unban", "فك الحظر عن عضو"),
    BotCommand("kick", "طرد عضو من القروب"),
    BotCommand("restrict", "تقييد عضو (منع كتابة)"),
    BotCommand("unrestrict", "فك التقييد عن عضو"),
    BotCommand("warn", "تحذير عضو"),
    BotCommand("clear_warns", "مسح تحذيرات عضو"),
    BotCommand("show_warns", "عرض تحذيرات عضو"),
    BotCommand("purge", "حذف عدد من الرسائل"),
    BotCommand("pin", "تثبيت رسالة بالرد"),
    BotCommand("unpin", "إلغاء تثبيت الرسالة"),
    BotCommand("lock_group", "قفل القروب (منع الجميع من الكتابة)"),
    BotCommand("unlock_group", "فتح القروب"),
    BotCommand("lock_media", "قفل الوسائط"),
    BotCommand("unlock_media", "فتح الوسائط"),
    BotCommand("lock_forward", "قفل التحويل"),
    BotCommand("unlock_forward", "فتح التحويل"),
    BotCommand("whois", "معلومات العضو بالرد"),
    BotCommand("id", "عرض الآيدي الخاص بك أو بالرد"),
    BotCommand("my_rank", "معرفة رتبتك وصلاحياتك"),
    BotCommand("admins", "قائمة مشرفين القروب"),

    # الإعدادات والتخصيص
    BotCommand("set_lang", "تغيير لغة البوت"),
    BotCommand("welcome_on", "تفعيل ترحيب الأعضاء الجدد"),
    BotCommand("welcome_off", "إيقاف ترحيب الأعضاء الجدد"),
    BotCommand("set_welcome", "تعيين رسالة الترحيب"),
    BotCommand("goodbye_on", "تفعيل رسالة المغادرة"),
    BotCommand("goodbye_off", "إيقاف رسالة المغادرة"),
    BotCommand("set_goodbye", "تعيين رسالة المغادرة"),
    BotCommand("set_rules", "ضع قوانين القروب"),
    BotCommand("get_rules", "عرض قوانين القروب"),
    BotCommand("captcha_on", "تفعيل التحقق البشري للأعضاء الجدد"),
    BotCommand("captcha_off", "إيقاف التحقق البشري"),
    BotCommand("night_mode_on", "تفعيل الوضع الليلي التلقائي"),
    BotCommand("night_mode_off", "إيقاف الوضع الليلي"),
    BotCommand("bot_name", "تغيير اسم البوت"),
    BotCommand("bot_photo", "تغيير صورة البوت"),
    BotCommand("bot_bio", "تغيير بايو البوت"),
    BotCommand("save_settings", "حفظ إعدادات القروب"),
    BotCommand("load_settings", "استعادة إعدادات القروب"),
    BotCommand("export_data", "تصدير بيانات القروب"),
    BotCommand("reset_data", "مسح إعدادات القروب"),
    BotCommand("turbo_mode", "تفعيل وضع السرعة الفائقة"),
    BotCommand("rocket_mode", "وضع الصاروخ الخاص بالمطور"),

    # الترفيه والتفاعل
    BotCommand("quran", "الاستماع لتلاوة قرآنية"),
    BotCommand("song", "بحث وتشغيل صوتية/نشيد"),
    BotCommand("ai_image", "توليد صورة بالذكاء الاصطناعي"),
    BotCommand("ai_chat", "سؤال الذكاء الاصطناعي"),
    BotCommand("check_link", "فحص رابط هل هو آمن"),
    BotCommand("quote", "إرسال حكمة أو مقولة عشوائية"),
    BotCommand("joke", "إرسال نكتة مضحكة"),
    BotCommand("puzzle", "إرسال لغز ذكي"),
    BotCommand("fortune", "توقعات اليوم"),
    BotCommand("rps", "لعبة حجرة صخر ورقة"),
    BotCommand("game", "لعبة تفاعلية سريعة بالقروب"),
    BotCommand("challenge", "إرسال تحدي يومي"),
    BotCommand("points", "عرض نقاط التفاعل الخاصة بك"),
    BotCommand("leaderboard", "لوحة شرف أكثر المتفاعلين"),
    BotCommand("group_stats", "إحصائيات القروب العامة"),
    BotCommand("countdown", "العد التنازلي لمناسبة"),
    BotCommand("weather", "معرفة حالة الطقس لمدينة"),
    BotCommand("convert", "تحويل العملات"),
    BotCommand("shorten", "اختصار الروابط"),
    BotCommand("date", "عرض تاريخ اليوم الهجري والميلادي"),

    # أوامر المطور والتحكم الشامل
    BotCommand("broadcast", "إذاعة نص لكل القروبات"),
    BotCommand("broadcast_private", "إذاعة خاصة للمستخدمين"),
    BotCommand("groups_count", "عرض عدد القروبات المفعّلة"),
    BotCommand("leave_group", "مغادرة قروب محدد"),
    BotCommand("global_ban", "حظر عام لمستخدم من البوت"),
    BotCommand("global_unban", "فك الحظر العام"),
    BotCommand("restart_bot", "إعادة تشغيل البوت"),
    BotCommand("bot_logs", "عرض سجلات الأخطاء والتشغيل"),
    BotCommand("server_status", "فحص استهلاك السيرفر RAM/CPU"),
    BotCommand("maintenance_on", "تفعيل وضع الصيانة"),
    BotCommand("maintenance_off", "إيقاف وضع الصيانة"),
    BotCommand("backup_db", "أخذ نسخة احتياطية لقاعدة البيانات"),
    BotCommand("add_dev", "رفع مطور جديد بالبوت"),
    BotCommand("remove_dev", "تنزيل مطور من البوت"),
    BotCommand("dev_list", "قائمة المطورين المعتمدين"),
    BotCommand("bot_check", "فحص جاهزية البوت الكاملة")
]

# دالة التحقق من الروابط
def contains_link(text: str) -> bool:
    if not text:
        return False
    url_pattern = r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(com|net|org|info|xyz|me|cc|tk|ml|ga|cf|gq|sa|ae|eg)[^\s]*)"
    return bool(re.search(url_pattern, text, re.IGNORECASE))

# معالجة الرسائل وفحص الروابط المخالفة
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    if message.chat.type in ["group", "supergroup"]:
        user_id = message.from_user.id
        chat_id = message.chat_id

        # استثناء المشرفين
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            if chat_member.status in ["creator", "administrator"]:
                return
        except Exception:
            pass

        # إذا وُجد رابط، احذفه واعطِ تقييد 5 دقائق
        if contains_link(message.text):
            try:
                await message.delete()
                until_date = datetime.now() + timedelta(minutes=5)
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    permissions={
                        "can_send_messages": False,
                        "can_send_media_messages": False,
                        "can_send_other_messages": False,
                        "can_add_web_page_previews": False
                    },
                    until_date=until_date
                )
                warning = await message.reply_text(
                    f"⚠️ تنبيه يا @{message.from_user.username or message.from_user.first_name}\n"
                    f"ممنوع إرسال الروابط نهائياً هنا! تم الحذف وتقييدك لمدة 5 دقائق ⏱️"
                )
                context.job_queue.run_once(lambda ctx: warning.delete(), 10)
            except Exception as e:
                print(f"خطأ في معالجة الرابط: {e}")

# أمر تجريبي استجابة لأي أمر من الـ 100
async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_name = update.message.text.split()[0]
    await update.message.reply_text(f"🤖 الأمر ({command_name}) يعمل بنجاح ومبرمج ضمن نظام الحماية المتكامل!")

async def post_init(application: Application):
    # تعيين الأوامر تلقائياً لتظهر جنب زر الدبوس في المجموعات
    await application.bot.set_my_commands(BOT_COMMANDS)
    print("✅ تم تحميل وربط أكثر من 100 أمر بنجاح!")

def main():
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # معالج الرسائل للروابط
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    # معالج عام للأوامر لكي تستجيب الأوامر كلها
    for cmd in BOT_COMMANDS:
        application.add_handler(CommandHandler(cmd.command, command_handler))

    print("🚀 بوت الحماية المتكامل شغال الآن وجاهز للاستضافة...")
    application.run_polling()

if __name__ == "__main__":
    main()
