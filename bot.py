# ==============================================================================
# 🌟 المشروع الأسطوري: البوت الرسمي الذكي (Telegram AI Bot - Aiogram & Gemini)
# ==============================================================================

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# --- إعدادات التوكن ومفتاح الذكاء الاصطناعي ---
TELEGRAM_BOT_TOKEN = "8797714829:AAFAGO7w2Y5Mgh_mPY4NWPtL8JlkEl_Fajc"
GEMINI_API_KEY = "AQ.Ab8RN6LDVdzfTMT89oU14HL7gnUayvWEtoYI3uhk02poijh2jw"

# تهيئة الذكاء الاصطناعي Gemini
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# إعداد البوت والمشغل
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# --- أوامر البوت الأساسية ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        " أهلاً بك! أنا بوت الذكاء الاصطناعي الخاص بك.\n"
        "يمكنك مراسلتي هنا في الخاص وسأقوم بالرد عليك وإجابتك على أي شيء فوراً! 🚀"
    )

# --- استقبال رسائل الخاص والرد عبر الذكاء الاصطناعي ---
@dp.message()
async def handle_all_messages(message: types.Message):
    # نتأكد أن الرسالة نصية وليست فارغة
    if not message.text:
        return
    
    try:
        # إرسال مؤشر الكتابة لكي يظهر للمستخدم أن البوت يكتب رد
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")
        
        # صياغة الطلب للذكاء الاصطناعي
        prompt = f"أنت مساعد ذكي ومحبوب تتحدث باللغة العربية بأسلوب طبيعي ومفيد جداً. أجب على رسالة المستخدم التالية: {message.text}"
        response = ai_model.generate_content(prompt)
        
        reply_text = response.text if response and response.text else "عذراً، لم أستطع صياغة إجابة، حاول مرة أخرى."
        
        # إرسال الرد للمستخدم في الخاص
        await message.answer(reply_text)
    except Exception as e:
        logging.error(f"AI Error: {e}")
        await message.answer("❌ حدث خطأ أثناء معالجة رسالتك بالذكاء الاصطناعي.")

# --- تشغيل البوت ---
async def main():
    print("=" * 60)
    print("🚀 [TELEGRAM AI BOT] البوت الرسمي يعمل الآن بكامل قوة Gemini!")
    print("=" * 60)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
