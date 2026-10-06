import re
from datetime import timedelta, datetime
from telegram import Update, BotCommand
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = "8797714829:AAFAGO7w2Y5Mgh_mPY4NWPtL8JlkEl_Fajc"

# قائمة الأوامر الأساسية والموثوقة
BOT_COMMANDS = [
    BotCommand("start", "تشغيل البوت وعرض القائمة"),
    BotCommand("help", "عرض المساعدة والأوامر"),
    BotCommand("protect_on", "تفعيل الحماية الكاملة"),
    BotCommand("protect_off", "إيقاف الحماية الكاملة"),
    BotCommand("links_block", "منع إرسال الروابط"),
    BotCommand("links_allow", "السماح بالروابط"),
    BotCommand("mute", "كتم عضو بالرد أو اليوزر"),
    BotCommand("unmute", "فك الكتم عن عضو"),
    BotCommand("ban", "حظر عضو من القروب"),
    BotCommand("unban", "فك الحظر عن عضو"),
    BotCommand("kick", "طرد عضو من القروب"),
    BotCommand("warn", "تحذير عضو"),
    BotCommand("clean", "مسح عدد من الرسائل"),
    BotCommand("pin", "تثبيت رسالة بالقروب"),
    BotCommand("lock_group", "قفل القروب (منع الكتابة)"),
    BotCommand("unlock_group", "فتح القروب للجميع"),
    BotCommand("id", "عرض الآيدي الخاص بك"),
    BotCommand("admins", "عرض قائمة مشرفي القروب"),
]

# دالة التحقق من الروابط
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

        # استثناء الأدمنيين
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            if chat_member.status in ["creator", "administrator"]:
                return
        except Exception:
            pass

        # إذا أرسل رابط: حذف + تقييد 5 دقائق
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
            except Exception as e:
                print(f"خطأ أثناء معالجة الرابط: {e}")

async def post_init(application: Application):
    # تعيين الأوامر مباشرة عند بدء تشغيل البوت
    try:
        await application.bot.set_my_commands(BOT_COMMANDS)
        print("✅ تم تعيين الأوامر بنجاح في قائمة الدبوس!")
    except Exception as e:
        print(f"تعذر تعيين الأوامر تلقائياً: {e}")

def main():
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("🚀 بوت الحماية المتكامل شغال الآن وجاهز للاستضافة...")
    application.run_polling()

if __name__ == "__main__":
    main()
