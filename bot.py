import asyncio
import html
import logging
import os
import random
import re
import sqlite3
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ChatMemberStatus, ChatType, ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, Message
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "").strip()
DB_PATH = os.getenv("DB_PATH", "guard.sqlite3")
MAX_WARNINGS = int(os.getenv("MAX_WARNINGS", "3"))
MUTE_MINUTES = int(os.getenv("MUTE_MINUTES", "60"))
ENABLE_CAPTCHA = os.getenv("ENABLE_CAPTCHA", "true").lower() == "true"
DELETE_LINKS = os.getenv("DELETE_LINKS", "true").lower() == "true"
DELETE_BAD_WORDS = os.getenv("DELETE_BAD_WORDS", "true").lower() == "true"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("telegram-guard")

URL_RE = re.compile(r"(?i)(https?://|www\.|t\.me/|telegram\.me/|@[a-z0-9_]{4,})")
FLOOD: dict[tuple[int, int], deque[float]] = defaultdict(lambda: deque(maxlen=12))
RECENT: dict[tuple[int, int], tuple[str, float]] = {}
PENDING_CAPTCHA: dict[tuple[int, int], int] = {}


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            title TEXT,
            rules TEXT DEFAULT 'احترم الجميع. يمنع السبام والروابط والإعلانات والمحتوى المخالف.',
            welcome TEXT DEFAULT 'أهلًا بك {name}! يرجى الضغط على زر التحقق للانضمام إلى المجموعة.',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS warnings (
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            last_reason TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (chat_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS filters (
            chat_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            PRIMARY KEY (chat_id, word)
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            user_id INTEGER,
            event TEXT NOT NULL,
            reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)


def ensure_chat(message: Message):
    with db() as con:
        con.execute("INSERT OR IGNORE INTO chats(chat_id, title) VALUES (?, ?)", (message.chat.id, message.chat.title or ""))
        con.execute("UPDATE chats SET title=? WHERE chat_id=?", (message.chat.title or "", message.chat.id))


def chat_setting(chat_id: int, key: str, default: str) -> str:
    with db() as con:
        row = con.execute(f"SELECT {key} FROM chats WHERE chat_id=?", (chat_id,)).fetchone()
    return row[key] if row and row[key] else default


def log_event(chat_id: int, user_id: int | None, event: str, reason: str = ""):
    with db() as con:
        con.execute("INSERT INTO events(chat_id,user_id,event,reason) VALUES (?,?,?,?)", (chat_id, user_id, event, reason))


async def is_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}
    except (TelegramBadRequest, TelegramForbiddenError):
        return False


async def punish(bot: Bot, message: Message, reason: str, delete: bool = True):
    if not message.from_user:
        return
    chat_id, user_id = message.chat.id, message.from_user.id
    try:
        if delete:
            await message.delete()
    except TelegramBadRequest:
        pass
    with db() as con:
        con.execute("INSERT INTO events(chat_id,user_id,event,reason) VALUES (?,?,?,?)", (chat_id, user_id, "violation", reason))
        row = con.execute("SELECT count FROM warnings WHERE chat_id=? AND user_id=?", (chat_id, user_id)).fetchone()
        count = (row["count"] if row else 0) + 1
        con.execute("INSERT INTO warnings(chat_id,user_id,count,last_reason) VALUES (?,?,?,?) ON CONFLICT(chat_id,user_id) DO UPDATE SET count=excluded.count,last_reason=excluded.last_reason,updated_at=CURRENT_TIMESTAMP", (chat_id, user_id, count, reason))
    if count >= MAX_WARNINGS:
        try:
            until = datetime.now(timezone.utc) + timedelta(minutes=MUTE_MINUTES)
            await bot.restrict_chat_member(chat_id, user_id, permissions=ChatPermissions(can_send_messages=False), until_date=until)
            action = f"تم كتمك لمدة {MUTE_MINUTES} دقيقة لتجاوز الحد ({MAX_WARNINGS}) من التحذيرات."
            log_event(chat_id, user_id, "mute", reason)
        except TelegramBadRequest:
            action = "تم تجاوز حد التحذيرات، لكن لا أملك صلاحية الكتم."
    else:
        action = f"تحذير {count}/{MAX_WARNINGS}: {reason}"
    try:
        notice = await message.answer(f"⚠️ <b>{html.escape(action)}</b>", parse_mode=ParseMode.HTML)
        await asyncio.sleep(7)
        await notice.delete()
    except TelegramBadRequest:
        pass


async def restrict_new_member(bot: Bot, message: Message):
    if not ENABLE_CAPTCHA or not message.new_chat_members:
        return
    for user in message.new_chat_members:
        if user.is_bot:
            continue
        key = (message.chat.id, user.id)
        answer = random.randint(1000, 9999)
        PENDING_CAPTCHA[key] = answer
        try:
            await bot.restrict_chat_member(message.chat.id, user.id, permissions=ChatPermissions(can_send_messages=False))
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"أنا لست روبوتًا: {answer}", callback_data=f"verify:{user.id}:{answer}")]])
            welcome = chat_setting(message.chat.id, "welcome", "أهلًا بك {name}! يرجى الضغط على زر التحقق للانضمام إلى المجموعة.").replace("{name}", html.escape(user.full_name))
            sent = await message.answer(welcome, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            asyncio.create_task(delete_later(sent, 600))
            log_event(message.chat.id, user.id, "captcha", "new member")
        except TelegramBadRequest:
            log.warning("لا أستطيع تقييد العضو %s في %s", user.id, message.chat.id)


async def delete_later(message: Message, seconds: int):
    await asyncio.sleep(seconds)
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def on_verify(callback: CallbackQuery, bot: Bot):
    if not callback.data or not callback.from_user or not callback.message:
        return
    _, raw_user, raw_answer = callback.data.split(":")
    if callback.from_user.id != int(raw_user):
        await callback.answer("هذا الزر مخصص للعضو الجديد.", show_alert=True)
        return
    key = (callback.message.chat.id, callback.from_user.id)
    if PENDING_CAPTCHA.get(key) != int(raw_answer):
        await callback.answer("انتهت صلاحية التحقق.", show_alert=True)
        return
    PENDING_CAPTCHA.pop(key, None)
    try:
        await bot.restrict_chat_member(callback.message.chat.id, callback.from_user.id, permissions=ChatPermissions(can_send_messages=True, can_send_audios=True, can_send_documents=True, can_send_photos=True, can_send_videos=True, can_send_video_notes=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True))
        await callback.message.edit_text(f"✅ تم التحقق من {html.escape(callback.from_user.full_name)}. أهلًا بك!", parse_mode=ParseMode.HTML)
        await callback.answer("تم التحقق بنجاح")
        log_event(callback.message.chat.id, callback.from_user.id, "verified", "captcha")
    except TelegramBadRequest:
        await callback.answer("تعذر إتمام التحقق. تأكد أن البوت مشرف.", show_alert=True)


async def command_admin(message: Message) -> bool:
    return bool(message.from_user and await is_admin(message.bot, message.chat.id, message.from_user.id))


async def require_admin(message: Message) -> bool:
    if message.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP} or not await command_admin(message):
        await message.reply("هذا الأمر للمشرفين فقط.")
        return False
    return True


async def target_user(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    return None


async def cmd_rules(message: Message):
    ensure_chat(message)
    await message.answer(chat_setting(message.chat.id, "rules", "لم يتم ضبط القواعد بعد."))


async def cmd_setrules(message: Message, command: CommandObject):
    if not await require_admin(message): return
    text = (command.args or "").strip()
    if not text:
        await message.reply("استخدم: /setrules نص القواعد")
        return
    with db() as con: con.execute("UPDATE chats SET rules=? WHERE chat_id=?", (text, message.chat.id))
    await message.reply("تم تحديث القواعد.")


async def cmd_setwelcome(message: Message, command: CommandObject):
    if not await require_admin(message): return
    text = (command.args or "").strip()
    if not text:
        await message.reply("استخدم: /setwelcome رسالة الترحيب (يمكن استخدام {name})")
        return
    with db() as con: con.execute("UPDATE chats SET welcome=? WHERE chat_id=?", (text, message.chat.id))
    await message.reply("تم تحديث رسالة الترحيب.")


async def cmd_warn(message: Message, reason: str = "مخالفة القواعد"):
    if not await require_admin(message): return
    user = await target_user(message)
    if not user or user.is_bot:
        await message.reply("استخدم الأمر بالرد على رسالة العضو.")
        return
    fake = message.model_copy(update={"from_user": user})
    await punish(message.bot, fake, reason, delete=False)


async def cmd_unwarn(message: Message):
    if not await require_admin(message): return
    user = await target_user(message)
    if not user: await message.reply("استخدم الأمر بالرد على رسالة العضو."); return
    with db() as con:
        con.execute("UPDATE warnings SET count=MAX(count-1,0) WHERE chat_id=? AND user_id=?", (message.chat.id, user.id))
    await message.reply("تمت إزالة تحذير واحد.")


async def cmd_warnings(message: Message):
    if not await require_admin(message): return
    user = await target_user(message)
    if not user: await message.reply("استخدم الأمر بالرد على رسالة العضو."); return
    with db() as con: row = con.execute("SELECT count,last_reason FROM warnings WHERE chat_id=? AND user_id=?", (message.chat.id, user.id)).fetchone()
    await message.reply(f"تحذيرات {user.full_name}: {(row['count'] if row else 0)}/{MAX_WARNINGS}\nالسبب الأخير: {(row['last_reason'] if row else 'لا يوجد')}")


async def cmd_mute(message: Message, command: CommandObject):
    if not await require_admin(message): return
    user = await target_user(message)
    if not user: await message.reply("استخدم الأمر بالرد على رسالة العضو."); return
    try: minutes = max(1, int((command.args or str(MUTE_MINUTES)).split()[0]))
    except ValueError: minutes = MUTE_MINUTES
    until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    try:
        await message.bot.restrict_chat_member(message.chat.id, user.id, permissions=ChatPermissions(can_send_messages=False), until_date=until)
        log_event(message.chat.id, user.id, "mute", f"manual {minutes}m")
        await message.reply(f"تم كتم {user.full_name} لمدة {minutes} دقيقة.")
    except TelegramBadRequest: await message.reply("تعذر الكتم. تحقق من صلاحيات البوت.")


async def cmd_unmute(message: Message):
    if not await require_admin(message): return
    user = await target_user(message)
    if not user: await message.reply("استخدم الأمر بالرد على رسالة العضو."); return
    perms = ChatPermissions(can_send_messages=True, can_add_web_page_previews=True, can_send_other_messages=True)
    try: await message.bot.restrict_chat_member(message.chat.id, user.id, permissions=perms); await message.reply("تم فك الكتم.")
    except TelegramBadRequest: await message.reply("تعذر فك الكتم.")


async def cmd_ban(message: Message):
    if not await require_admin(message): return
    user = await target_user(message)
    if not user: await message.reply("استخدم الأمر بالرد على رسالة العضو."); return
    try: await message.bot.ban_chat_member(message.chat.id, user.id); log_event(message.chat.id, user.id, "ban", "manual"); await message.reply("تم حظر العضو.")
    except TelegramBadRequest: await message.reply("تعذر الحظر. تحقق من صلاحيات البوت.")


async def cmd_unban(message: Message, command: CommandObject):
    if not await require_admin(message): return
    try: user_id = int((command.args or "").strip())
    except ValueError: await message.reply("استخدم: /unban رقم_المستخدم"); return
    try: await message.bot.unban_chat_member(message.chat.id, user_id, only_if_banned=True); await message.reply("تم فك الحظر.")
    except TelegramBadRequest: await message.reply("تعذر فك الحظر.")


async def cmd_filter(message: Message, command: CommandObject, add: bool):
    if not await require_admin(message): return
    word = (command.args or "").strip().lower()
    if not word: await message.reply("اكتب الكلمة بعد الأمر."); return
    with db() as con:
        if add: con.execute("INSERT OR IGNORE INTO filters(chat_id,word) VALUES (?,?)", (message.chat.id, word))
        else: con.execute("DELETE FROM filters WHERE chat_id=? AND word=?", (message.chat.id, word))
    await message.reply("تمت إضافة الكلمة إلى الفلتر." if add else "تم حذف الكلمة من الفلتر.")


async def cmd_filters(message: Message):
    if not await require_admin(message): return
    with db() as con: rows = con.execute("SELECT word FROM filters WHERE chat_id=? ORDER BY word", (message.chat.id,)).fetchall()
    await message.reply("الكلمات الممنوعة: " + (", ".join(r["word"] for r in rows) if rows else "لا توجد"))


async def cmd_settings(message: Message):
    if not await require_admin(message): return
    await message.reply(f"إعدادات الحماية:\n- الكابتشا: {'مفعلة' if ENABLE_CAPTCHA else 'معطلة'}\n- حذف الروابط: {'مفعل' if DELETE_LINKS else 'معطل'}\n- حد التحذيرات: {MAX_WARNINGS}\n- مدة الكتم: {MUTE_MINUTES} دقيقة")


async def cmd_stats(message: Message):
    if not await require_admin(message): return
    with db() as con:
        violations = con.execute("SELECT COUNT(*) c FROM events WHERE chat_id=? AND event='violation'", (message.chat.id,)).fetchone()["c"]
        mutes = con.execute("SELECT COUNT(*) c FROM events WHERE chat_id=? AND event='mute'", (message.chat.id,)).fetchone()["c"]
        bans = con.execute("SELECT COUNT(*) c FROM events WHERE chat_id=? AND event='ban'", (message.chat.id,)).fetchone()["c"]
    await message.reply(f"إحصاءات المجموعة:\nالمخالفات المحذوفة: {violations}\nعمليات الكتم: {mutes}\nعمليات الحظر: {bans}")


async def moderate_message(message: Message):
    if message.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP} or not message.from_user:
        return
    ensure_chat(message)
    if await is_admin(message.bot, message.chat.id, message.from_user.id):
        return
    text = message.text or message.caption or ""
    key = (message.chat.id, message.from_user.id)
    now = time.monotonic()
    if URL_RE.search(text) and DELETE_LINKS:
        await punish(message.bot, message, "نشر رابط أو إعلان", delete=True)
        return
    with db() as con:
        words = [r["word"] for r in con.execute("SELECT word FROM filters WHERE chat_id=?", (message.chat.id,)).fetchall()]
    if DELETE_BAD_WORDS and any(word in text.casefold() for word in words):
        await punish(message.bot, message, "كلمة ممنوعة", delete=True)
        return
    times = FLOOD[key]
    times.append(now)
    if len(times) >= 6 and now - times[-6] <= 10:
        await punish(message.bot, message, "إرسال رسائل بسرعة (سبام)", delete=True)
        times.clear()
        return
    normalized = re.sub(r"\s+", " ", text.strip().casefold())
    previous = RECENT.get(key)
    RECENT[key] = (normalized, now)
    if normalized and previous and previous[0] == normalized and now - previous[1] <= 30:
        await punish(message.bot, message, "تكرار الرسالة", delete=True)


async def main():
    if not TOKEN or TOKEN == "ضع_توكن_البوت_هنا":
        raise SystemExit("ضع BOT_TOKEN في ملف .env أولًا")
    init_db()
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    router = Router()
    router.message.register(cmd_rules, Command("rules"))
    router.message.register(cmd_setrules, Command("setrules"))
    router.message.register(cmd_setwelcome, Command("setwelcome"))
    router.message.register(lambda m: cmd_warn(m), Command("warn"))
    router.message.register(cmd_unwarn, Command("unwarn"))
    router.message.register(cmd_warnings, Command("warnings"))
    router.message.register(cmd_mute, Command("mute"))
    router.message.register(cmd_unmute, Command("unmute"))
    router.message.register(cmd_ban, Command("ban"))
    router.message.register(cmd_unban, Command("unban"))
    router.message.register(lambda m, c: cmd_filter(m, c, True), Command("filterword"))
    router.message.register(lambda m, c: cmd_filter(m, c, False), Command("unfilterword"))
    router.message.register(cmd_filters, Command("filters"))
    router.message.register(cmd_settings, Command("settings"))
    router.message.register(cmd_stats, Command("stats"))
    router.callback_query.register(on_verify, F.data.startswith("verify:"))
    router.message.register(restrict_new_member, F.new_chat_members)
    router.message.register(moderate_message)
    dp.include_router(router)
    log.info("البوت يعمل")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
