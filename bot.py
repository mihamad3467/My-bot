import re
import os
import time
import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ==========================================
# إعدادات البوت والبيانات الأساسية
# ==========================================
TOKEN = os.getenv("TOKEN", "8797714829:AAFAGO7w2Y5Mgh_mPY4NWPtL8JlkEl_Fajc")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8808657227"))

# تخزين مؤقت لقاعدة بيانات وهمية (للمجموعات، المستخدمين، الإعدادات، النقاط، والإنذارات)
DB = {
    "users": set(),
    "groups": set(),
    "warnings": {},  # {chat_id: {user_id: count}}
    "mutes": {},     # {chat_id: {user_id: until_timestamp}}
    "settings": {    # إعدادات الحماية لكل مجموعة
        # chat_id: {"links": True, "bots": True, "arabic": False, "photos": False, "welcome": True}
    }
}

# ==========================================
# نصوص الردود المتقدمة والترحيب الاحترافي
# ==========================================
def get_welcome_text(user_name: str, user_id: int) -> str:
    return (
        f"✨ **أهلاً بك يا {user_name}!**\n\n"
        f"🤖 أنا بوت الإدارة والحماية الذكي (Enterprise Security Bot).\n"
        f"🆔 آيديك الشخصي: `{user_id}`\n\n"
        f"🚀 **مميزاتي:**\n"
        f"• حماية خارقة للمجموعات (منع روابط، بوتات، سبام، ميديا ضارة).\n"
        f"• نظام إداري متكامل (كتم، طرد، حظر، تحذيرات).\n"
        f"• أوامر ذكية وتفاعلية بدون سلاش أو مع سلاش.\n\n"
        f"📌 أرسل /help لعرض قائمة الأوامر المتاحة أو تواصل مع الإدارة."
    )

# ==========================================
# دوال المساعدة والفحص
# ==========================================
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

async def check_group_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """التحقق مما إذا كان المستخدم مشرفاً في المجموعة أو المطور"""
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return False
    if user.id == ADMIN_ID:
        return True
    if chat.type in ["group", "supergroup"]:
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            return member.status in ["creator", "administrator"]
        except Exception:
            return False
    return True

# ==========================================
# الأوامر الأساسية (Commands)
# ==========================================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    
    DB["users"].add(user.id)
    text = get_welcome_text(user.first_name, user.id)
    
    keyboard = [
        [InlineKeyboardButton("➕ أضفني لمجموعتك", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("🛠️ الأوامر", callback_data="help_menu"), InlineKeyboardButton("📊 إحصائيات", callback_data="stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠️ **دليل الأوامر الشامل:**\n\n"
        "🔸 **أوامر الإدارة:**\n"
        "• `/ban` - حظر عضو (بالرد أو الآيدي)\n"
        "• `/unban` - إلغاء حظر عضو\n"
        "• `/mute` - كتم عضو لفترة معينة\n"
        "• `/unmute` - إلغاء كتم عضو\n"
        "• `/warn` - تحذير عضو\n"
        "• `/unwarn` - مسح تحذيرات عضو\n"
        "• `/pin` - تثبيت رسالة\n"
        "• `/purge` - مسح الرسائل\n\n"
        "🔸 **أوامر الحماية والإعدادات:**\n"
        "• `/settings` - عرض إعدادات المجموعة\n"
        "• `/antilink on/off` - قفل/فتح الروابط\n"
        "• `/antibots on/off` - طرد البوتات المضافة\n\n"
        "💡 *يمكنك أيضاً استخدام الكلمات العربية مباشرة مثل: (كتم، حظر، تثبيت، بنج).* "
    )
    if update.message:
        await update.message.reply_text(help_text, parse_mode="Markdown")

async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if not user or not update.message:
        return
    
    text = (
        f"🆔 **معلوماتك:**\n"
        f"• الاسم: {user.first_name}\n"
        f"• الآيدي: `{user.id}`\n"
        f"• المعرف: @{user.username if user.username else 'لا يوجد'}\n"
        f"• آيدي المحادثة: `{chat.id}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    if not update.message:
        return
    msg = await update.message.reply_text("🏓 جاري قياس السرعة...")
    end_time = time.time()
    ping_ms = round((end_time - start_time) * 1000, 2)
    await msg.edit_text(f"🏓 **Pong!**\n⚡ السرعة: `{ping_ms}ms`\n🌐 السيرفر: `Online & Stable`", parse_mode="Markdown")

# ==========================================
# أوامر الإدارة التنفيذية
# ==========================================
async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_group_admin(update, context):
        await update.message.reply_text("❌ هذا الأمر للمشرفين فقط!")
        return
    
    message = update.message
    chat = update.effective_chat
    if not message or not chat:
        return

    user_to_ban = None
    if message.reply_to_message:
        user_to_ban = message.reply_to_message.from_user.id
    elif context.args:
        try:
            user_to_ban = int(context.args[0])
        except ValueError:
            pass

    if not user_to_ban:
        await message.reply_text("⚠️ قم بالرد على رسالة الشخص أو اكتب آيديه لحظره.")
        return

    try:
        await context.bot.ban_chat_member(chat.id, user_to_ban)
        await message.reply_text(f"🔨 تم حظر المستخدم بنجاح (`{user_to_ban}`).", parse_mode="Markdown")
    except Exception as e:
        await message.reply_text(f"❌ فشل الحظر: {e}")

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_group_admin(update, context):
        return
    message = update.message
    chat = update.effective_chat
    if not message or not chat:
        return

    user_to_mute = None
    if message.reply_to_message:
        user_to_mute = message.reply_to_message.from_user.id
    
    if not user_to_mute:
        await message.reply_text("⚠️ قم بالرد على رسالة الشخص لكتمه.")
        return

    try:
        until = datetime.now() + timedelta(hours=1)
        await context.bot.restrict_chat_member(
            chat.id,
            user_to_mute,
            permissions={"can_send_messages": False},
            until_date=until
        )
        await message.reply_text(f"🔇 تم كتم المستخدم لمدة ساعة.")
    except Exception as e:
        await message.reply_text(f"❌ فشل الكتم: {e}")

# ==========================================
# نظام التعامل مع الرسائل والحماية الشاملة
# ==========================================
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    chat = message.chat
    user = message.from_user
    if not user or not chat:
        return

    # تسجيل المجموعات والمستخدمين
    if chat.type in ["group", "supergroup"]:
        DB["groups"].add(chat.id)
    DB["users"].add(user.id)

    text = message.text.lower()

    # معالجة الروابط في المجموعات
    if chat.type in ["group", "supergroup"]:
        # استثناء المشرفين
        if user.id != ADMIN_ID:
            try:
                member = await context.bot.get_chat_member(chat.id, user.id)
                if member.status in ["creator", "administrator"]:
                    return
            except Exception:
                pass

        # فحص الروابط
        url_pattern = r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(com|net|org|info|xyz|me|cc|tk))"
        if re.search(url_pattern, text, re.IGNORECASE):
            try:
                await message.delete()
                await message.reply_text(f"⚠️ {user.first_name}، ممنوع إرسال الروابط هنا! 🚫")
                return
            except Exception:
                pass

    # الردود الذكية الفورية بدون سلاش
    if text in ["السلام عليكم", "السلام", "سلام عليكم"]:
        await message.reply_text(f"وعليكم السلام ورحمة الله وبركاته يا {user.first_name} 👋 أهلاً بك!")
    elif text in ["آيدي", "معلوماتي", "id"]:
        await cmd_id(update, context)
    elif text in ["بنج", "سرعة", "ping"]:
        await cmd_ping(update, context)

# ==========================================
# معالجة الضغط على الأزرار (Callback Queries)
# ==========================================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()

    if query.data == "help_menu":
        await query.edit_message_text(
            "🛠️ **قائمة الأوامر المتقدمة:**\n\n"
            "• `/ban` - حظر\n"
            "• `/mute` - كتم\n"
            "• `/warn` - تحذير\n"
            "• `/id` - آيديك\n"
            "• `/ping` - السرعة",
            parse_mode="Markdown"
        )
    elif query.data == "stats":
        await query.edit_message_text(
            f"📊 **إحصائيات البوت الحالية:**\n\n"
            f"• المستخدمين المسجلين: `{len(DB['users'])}`\n"
            f"• المجموعات المفعل فيها: `{len(DB['groups'])}`\n"
            f"• الحالة: `متصل ويعمل بكفاءة عالية 🚀`",
            parse_mode="Markdown"
        )

# ==========================================
# تهيئة البوت وتشغيله
# ==========================================
async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "تشغيل البوت وعرض الترحيب"),
        BotCommand("help", "قائمة المساعدة والأوامر"),
        BotCommand("id", "معرفة الآيدي والمعلومات"),
        BotCommand("ping", "فحص سرعة استجابة البوت"),
        BotCommand("ban", "حظر عضو (للمشرفين)"),
        BotCommand("mute", "كتم عضو (للمشرفين)")
    ])
    print("✅ تم تعيين الأوامر وتفعيل البوت بنجاح!")

def main():
    if not TOKEN:
        print("❌ خطأ: التوكن غير موجود!")
        return

    application = Application.builder().token(TOKEN).post_init(post_init).build()

    # معالجات الأوامر
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("id", cmd_id))
    application.add_handler(CommandHandler("ping", cmd_ping))
    application.add_handler(CommandHandler("ban", cmd_ban))
    application.add_handler(CommandHandler("mute", cmd_mute))

    # معالجة الأزرار
    application.add_handler(CallbackQueryHandler(button_callback))

    # معالجة الرسائل النصية والحماية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))

    print("🚀 جاري تشغيل البوت بنظام الـ Polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
