import re
from datetime import timedelta, datetime
from telegram import Update, BotCommand
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# التوكن والآيدي الخاص بالمطور الفخم محمد (@dl_r7c)
TOKEN = "8797714829:AAFAGO7w2Y5Mgh_mPY4NWPtL8JlkEl_Fajc"
ADMIN_ID = 8808657227  

# قائمة الأوامر الشاملة (أكثر من 10+ أوامر أساسية واحترافية)
BOT_COMMANDS = [
    BotCommand("start", "تشغيل البوت وعرض لوحة التحكم"),
    BotCommand("help", "عرض قائمة الأوامر والمساعدة"),
    BotCommand("id", "معرفة الآيدي الخاص بك أو بالرسالة"),
    BotCommand("ping", "فحص سرعة استجابة البوت"),
    BotCommand("ban", "حظر عضو (رد على رسالته)"),
    BotCommand("unban", "إلغاء حظر عضو (بالآيدي)"),
    BotCommand("mute", "تقييد عضو (رد على رسالته)"),
    BotCommand("unmute", "إلغاء تقييد عضو"),
    BotCommand("kick", "طرد عضو من المجموعة"),
    BotCommand("del", "حذف رسالة محددة"),
    BotCommand("dev", "معلومات المطور الصانع"),
]

# دالة فحص الروابط
def contains_link(text: str) -> bool:
    if not text:
        return False
    url_pattern = r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(com|net|org|info|xyz|me|cc|tk|ml|ga|cf|gq)[^\s]*)"
    return bool(re.search(url_pattern, text, re.IGNORECASE))

# أمر /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id == ADMIN_ID:
        await update.message.reply_text(
            f"👑 **أهلاً ومرحباً بمطوري وصانعي الفخم محمد (@dl_r7c)!**\n\n"
            f"البوت يعمل بكامل طاقته ومزود بصلاحيات الإدارة الكاملة والحماية والتحكم. آمرني بما شئت يا بطل! 🚀",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"مرحباً بك يا {user.first_name} في بوت الحماية والإدارة الشامل! 🛡️\n"
            f"استخدم /help لعرض الأوامر المتاحة."
        )

# أمر /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠️ **قائمة الأوامر المتاحة:**\n\n"
        "🔸 `/start` - تشغيل البوت\n"
        "🔸 `/help` - عرض المساعدة\n"
        "🔸 `/id` - معرفة الآيدي\n"
        "🔸 `/ping` - حالة البوت وسرعته\n\n"
        "🛡️ **أوامر الإدارة (للمشرفين والمطور):**\n"
        "🔹 `/ban` - حظر (بالرد على الرسالة)\n"
        "🔹 `/unban [id]` - إلغاء الحظر\n"
        "🔹 `/mute` - كتم وتقييد (بالرد)\n"
        "🔹 `/unmute` - رفع التقييد (بالرد)\n"
        "🔹 `/kick` - طرد (بالرد)\n"
        "🔹 `/del` - حذف الرسالة المردود عليها\n"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# أمر /id
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        await message.reply_text(f"🆔 آيدي العضو {target_user.first_name} هو: `{target_user.id}`", parse_mode="Markdown")
    else:
        user = update.effective_user
        await message.reply_text(f"🆔 الآيدي الخاص بك هو: `{user.id}`", parse_mode="Markdown")

# أمر /ping
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! البوت يعمل بكفاءة عالية وصاروخية 🚀")

# أمر /dev
async def dev_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💻 هذا البوت تم تصميمه وبرمجته خصيصاً بواسطة المطور الفخم محمد (@dl_r7c).")

# أمر الحظر /ban
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        # فحص إذا كان مشرف
        try:
            member = await context.bot.get_chat_member(message.chat_id, user_id)
            if member.status not in ["creator", "administrator"]:
                await message.reply_text("⚠️ هذا الأمر للمشرفين والمطور فقط!")
                return
        except:
            return

    if not message.reply_to_message:
        await message.reply_text("⚠️ يجب الرد على رسالة الشخص المراد حظره!")
        return

    target_id = message.reply_to_message.from_user.id
    if target_id == ADMIN_ID:
        await message.reply_text("❌ لا يمكنك حظر مطوري وصانعي محمد!")
        return

    try:
        await context.bot.ban_chat_member(message.chat_id, target_id)
        await message.reply_text("🔨 تم حظر المستخدم بنجاح!")
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ: {e}")

# أمر الكتم /mute
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id

    if user_id != ADMIN_ID:
        try:
            member = await context.bot.get_chat_member(message.chat_id, user_id)
            if member.status not in ["creator", "administrator"]:
                await message.reply_text("⚠️ هذا الأمر للمشرفين والمطور فقط!")
                return
        except:
            return

    if not message.reply_to_message:
        await message.reply_text("⚠️ يجب الرد على رسالة الشخص المراد كتمه!")
        return

    target_id = message.reply_to_message.from_user.id
    if target_id == ADMIN_ID:
        await message.reply_text("❌ لا يمكنك كتم مطوري وصانعي محمد!")
        return

    try:
        until_date = datetime.now() + timedelta(hours=1)
        await context.bot.restrict_chat_member(
            chat_id=message.chat_id,
            user_id=target_id,
            permissions={"can_send_messages": False},
            until_date=until_date
        )
        await message.reply_text("🔇 تم كتم المستخدم لمدة ساعة بنجاح!")
    except Exception as e:
        await message.reply_text(f"❌ حدث خطأ: {e}")

# أمر الحذف /del
async def del_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception as e:
            await message.reply_text(f"❌ لا يمكنني حذف الرسالة: {e}")

# معالجة الرسائل والروابط
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    if message.chat.type in ["group", "supergroup"]:
        user_id = message.from_user.id
        chat_id = message.chat_id

        if user_id == ADMIN_ID:
            return

        try:
            chat_member = await context.bot.get_chat_member(chat_id, user_id)
            if chat_member.status in ["creator", "administrator"]:
                return
        except Exception:
            pass

        # حظر الروابط التلقائي
        if contains_link(message.text):
            try:
                await message.delete()
                until_date = datetime.now() + timedelta(minutes=10)
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    permissions={"can_send_messages": False},
                    until_date=until_date
                )
                await message.reply_text(f"⚠️ ممنوع إرسال الروابط هنا! تم الحذف وتقييد العضو 10 دقائق ⏱️")
            except Exception as e:
                print(f"خطأ: {e}")

async def post_init(application: Application):
    await application.bot.set_my_commands(BOT_COMMANDS)
    print("✅ تم تعيين جميع الأوامر بنجاح!")

def main():
    application = Application.builder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("dev", dev_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("del", del_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("🚀 البوت الشامل يعمل الآن بكامل طاقته...")
    application.run_polling()

if __name__ == "__main__":
    main()
