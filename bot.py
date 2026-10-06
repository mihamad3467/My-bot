import re
from datetime import timedelta, datetime
from telegram import Update, BotCommand
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# التوكن وآيدي المطور محمد (dl_r7c)
TOKEN = "8797714829:AAFAGO7w2Y5Mgh_mPY4NWPtL8JlkEl_Fajc"
ADMIN_ID = 8808657227  

# قائمة الأوامر المعتمدة
BOT_COMMANDS = [
    BotCommand("start", "تشغيل البوت وعرض القائمة"),
    BotCommand("help", "عرض المساعدة والأوامر"),
    BotCommand("id", "عرض الآيدي الخاص بك"),
]

# دالة فحص الروابط
def contains_link(text: str) -> bool:
    if not text:
        return False
    url_pattern = r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(com|net|org|info|xyz|me|cc|tk|ml|ga|cf|gq)[^\s]*)"
    return bool(re.search(url_pattern, text, re.IGNORECASE))

# رد على أمر /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID:
        await update.message.reply_text(f"أهلاً ومرحباً بمطوري وصانعي الفخم محمد (@dl_r7c)! 👑🤖 البوت تحت أمرك بالكامل.")
    else:
        await update.message.reply_text(f"مرحباً بك يا {user.first_name} في بوت حماية المجموعات! 🛡️")

# رد على أمر /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠️ الأوامر المتاحة: /start, /help, /id")

# رد على أمر /id
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🆔 الآيدي الخاص بك هو: `{user.id}`", parse_mode="Markdown")

# معالجة الرسائل والروابط
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    if message.chat.type in ["group", "supergroup"]:
        user_id = message.from_user.id
        chat_id = message.chat_id

        # استثناء المطور
        if user_id == ADMIN_ID:
            return

        try:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            if chat_member.status in ["creator", "administrator"]:
                return
        except Exception:
            pass

        # إذا أرسل رابط: حذف + تقييد
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
                await message.reply_text(f"⚠️ ممنوع إرسال الروابط هنا! تم حذف الرابط وتقييدك 5 دقائق ⏱️")
            except Exception as e:
                print(f"خطأ: {e}")

async def post_init(application: Application):
    await application.bot.set_my_commands(BOT_COMMANDS)
    print("✅ تم تعيين الأوامر بنجاح!")

def main():
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("🚀 البوت شغال الآن...")
    application.run_polling()

if __name__ == "__main__":
    main()
