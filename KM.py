import logging
import asyncio
import os
import re
import sys
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web

# --- KONFIGURATSIYA ---
API_TOKEN = '8695645149:AAGBV002oQ2hHBEBrV3YkXGNisLOhcpUeyY'
GROUP_1_ID = -1003696980644  
GROUP_2_ID = -1003844822699

# Xodimlar ro'yxati
STAFF_LIST = [
    "@eldorchik24",
    "@OYBEK_88_00",
    "@Diyor_Yusupov86"
]

# Boshlash buyruqlari
START_COMMANDS = ["proyekt", "proekt","22","33","11", "km"]

# Global o'zgaruvchilar
current_index = 0
is_session_active = False
current_staff_username = None
forwarded_count = 0  # Sessiya davomida 2-guruhga nechta xabar o'tkazildi

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- PLATFORMA MOSLASHUVCHANLIGI ---
# Windows tizimida asyncio xatolarini oldini olish uchun
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# --- RENDER WEB SERVER (DUMMY) ---
async def handle(request):
    return web.Response(text="KM Bot is Active and Healthy!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render PORT muhit o'zgaruvchisidan foydalanadi, localda esa 8080
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")

# --- BOT MANTIQI ---
@dp.message(F.chat.id == GROUP_1_ID)
async def session_handler(message: types.Message):
    global current_index, is_session_active, current_staff_username, forwarded_count
    
    # Xabar matnini aniqlash
    raw_text = message.text.strip() if message.text else ""
    # Agar matn bo'lmasa rasm caption'ini tekshirish
    if not raw_text and message.caption:
        raw_text = message.caption.strip()
        
    msg_text = raw_text.lower().replace(" ", "")

    # 1. Sessiyani boshlash
    if any(cmd == msg_text for cmd in START_COMMANDS):
        is_session_active = True
        forwarded_count = 0  # Yangi sessiya — hisoblagichni nolga tushiramiz
        current_staff_username = STAFF_LIST[current_index % len(STAFF_LIST)]
        await message.reply(
            f"🚀 <b>Yangi sessiya boshlandi!</b>\n"
            f"Mas'ul xodim: <b>{current_staff_username}</b>", 
            parse_mode="HTML"
        )
        return

    # 2. Sessiyani tugatish (✅)
    if raw_text and "✅" in raw_text:
        # Harf yoki raqam yo'qligini tekshirish (faqat emoji bo'lsa tugatadi)
        has_alphanumeric = bool(re.search(r'[a-zA-Z0-9а-яА-Я]', raw_text))
        if not has_alphanumeric:
            if is_session_active:
                if forwarded_count > 0:
                    # Haqiqiy vazifa o'tkazilgan → navbat keyingi xodimga o'tadi
                    await message.reply(
                        f"🛑 <b>Sessiya yakunlandi.</b>\n"
                        f"Navbat keyingi xodimga o'tdi.", 
                        parse_mode="HTML"
                    )
                    current_index = (current_index + 1) % len(STAFF_LIST)
                else:
                    # Hech narsa o'tkazilmadi (adashib ochilgan) → navbat o'sha xodimda qoladi
                    await message.reply(
                        f"↩️ <b>Sessiya bekor qilindi.</b>\n"
                        f"Vazifa o'tkazilmadi — navbat <b>{current_staff_username}</b> da qoldi.", 
                        parse_mode="HTML"
                    )
                is_session_active = False
                current_staff_username = None
                forwarded_count = 0
            return

    # 3. Fayllarni o'tkazish
    if is_session_active:
        # Buyruqlarni o'zini o'tkazib yubormaslik uchun
        if msg_text in START_COMMANDS:
            return

        mention_tag = f"\n\n🎯 <b>Mas'ul:</b> {current_staff_username}"
        try:
            # Agar xabar faqat matn bo'lsa
            if message.text:
                await bot.send_message(
                    chat_id=GROUP_2_ID, 
                    text=message.text + mention_tag, 
                    parse_mode="HTML"
                )
            # Rasm, video yoki hujjat bo'lsa
            else:
                await bot.copy_message(
                    chat_id=GROUP_2_ID,
                    from_chat_id=GROUP_1_ID,
                    message_id=message.message_id,
                    caption=(message.caption or "") + mention_tag,
                    parse_mode="HTML"
                )
            forwarded_count += 1  # Muvaffaqiyatli o'tkazildi — hisoblagichni oshiramiz
        except Exception as e:
            logging.error(f"Xabar yuborishda xato: {e}")

# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    # Web serverni fonda yurgizamiz
    asyncio.create_task(start_web_server())
    
    # Konfliktlarni oldini olish uchun eski yangilanishlarni o'chirish
    await bot.delete_webhook(drop_pending_updates=True)
    
    logging.info("🚀 KM Bot ishga tushishga tayyor...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Polling xatosi: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.")
