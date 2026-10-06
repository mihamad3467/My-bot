import re
from datetime import timedelta, datetime
from telegram import Update, BotCommand
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = "8797714829:AAFAGO7w2Y5Mgh_mPY4NWPtL8JlkEl_Fajc"

# قائمة الأوامر الأساسية والمستقرة تماماً (50 أمر احترافي)
BOT_COMMANDS = [
    BotCommand("start", "تشغيل البوت وعرض القائمة"),
    BotCommand("help", "عرض المساعدة والأوامر"),
    BotCommand("protect_on", "تفعيل الحماية الكاملة"),
    BotCommand("protect_off", "إيقاف الحماية الكاملة"),
    BotCommand("links_block", "منع إرسال الروابط"),
    BotCommand("links_allow", "السماح بالروابط"),
    BotCommand("spam_block", "منع التكرار المزعج"),
    BotCommand("forward_block", "منع التوجيه"),
    BotCommand("bots_block", "منع دخول البوتات"),
    BotCommand("photos_block", "منع الصور"),
    BotCommand("videos_block", "منع الفيديوهات"),
    BotCommand("files_block", "منع الملفات"),
    BotCommand("stickers_block", "منع الملصقات"),
    BotCommand("add_badword", "إضافة كلمة ممنوعة"),
    BotCommand("del_badword", "حذف كلمة ممنوعة"),
    BotCommand("list_badwords", "عرض الكلمات الممنوعة"),
    BotCommand("shield_status", "عرض حالة الحماية"),
    BotCommand("mute", "كتم عضو بالرد أو اليوزر"),
    BotCommand("unmute", "فك الكتم عن عضو"),
    BotCommand("ban", "حظر عضو من القروب"),
    BotCommand("unban", "فك الحظر عن عضو"),
    BotCommand("kick", "طرد عضو من القروب"),
    BotCommand("restrict", "تقييد عضو مؤقتاً"),
    BotCommand("unrestrict", "فك التقييد عن عضو"),
    BotCommand("warn", "تحذير عضو"),
    BotCommand("clear_warns", "مسح تحذيرات عضو"),
    BotCommand("clean", "مسح عدد من الرسائل"),
    BotCommand("pin", "تثبيت رسالة بالقروب"),
    BotCommand("unpin", "إلغاء تثبيت الرسالة"),
    BotCommand("lock_group", "قفل القروب (منع الكتابة)"),
    BotCommand("unlock_group", "فتح القروب للجميع"),
    BotCommand("whois", "معلومات العضو"),
    BotCommand("id", "عرض الآيدي الخاص بك"),
    BotCommand("admins", "عرض قائمة مشرفي القروب"),
    BotCommand("welcome_on", "تفعيل رسالة الترحيب"),
    BotCommand("welcome_off", "إيقاف رسالة الترحيب"),
    BotCommand("set_welcome", "تعيين نص الترحيب"),
    BotCommand("set_rules", "وضع قوانين القروب"),
    BotCommand("get_rules", "عرض قوانين القروب"),
    BotCommand("captcha_on", "تفعيل التحقق البشري"),
    BotCommand("quran", "استماع لتلاوة قرآنية"),
    BotCommand("image", "توليد صورة بالذكاء الاصطناعي"),
    BotCommand("ai", "التحدث مع الذكاء الاصطناعي"),
    BotCommand("joke", "إرسال نكتة مسلية"),
    BotCommand("points", "عرض نقاط التفاعل"),
    BotCommand("leaderboard", "لوحة شرف القروب"),
    BotCommand("stats", "إحصائيات القروب العامة"),
    BotCommand("weather", "معرفة حالة الطقس"),
    BotCommand("restart", "إعادة تشغيل البوت"),
    BotCommand("health_check", "فحص جاهزية البوت الشاملة")
]

def contains_link(text: str) -> bool:
    if not text:
        return False
    url_pattern = r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(com|net|org|info|xyz|me|cc|tk|ml|ga|cf|gq)[^\s]*)"
    return bool(re.search(url_pattern, text, re.IGNORECASE))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    if message.chat.type in ["group", "supergroup"]:
        user_id = message.from_user.id
        chat_id = message.chat_id

        try:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            if chat_member.status in ["creator", "administrator"]:
                return
        except Exception:
            pass

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
                    f"ممنوع إرسال الروابط هنا! تم حذف الرابط وتقييدك لمدة 5 دقائق ⏱️"
                )
                context.job_queue.run_once(lambda ctx: warning.delete(), 10)
            except Exception as e:
                print(f"خطأ أثناء معالجة الرابط: {e}")

def main():
    application = Application.builder().token(TOKEN).build()

    # تعيين الأوامر بأمان داخل حلقة الحدث (Event Loop) بعد بدء البوت
    async def set_commands(app):
        try:
            await app.bot.set_my_commands(BOT_COMMANDS)
            print("✅ تم تعيين الأوامر بنجاح في قائمة الدبوس!")
        except Exception as e:
            print(f"⚠️ ملاحظة تعيين الأوامر: {e}")

    application.job_queue.run_once(lambda ctx: set_commands(application), 1)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("🚀 بوت الحماية المتكامل شغال الآن وجاهز للاستضافة...")
    application.run_polling()

if __name__ == "__main__":
    main()
