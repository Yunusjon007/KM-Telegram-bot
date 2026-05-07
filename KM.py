import logging
import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web

# --- KONFIGURATSIYA ---
API_TOKEN = '8695645149:AAGBV002oQ2hHBEBrV3YkXGNisLOhcpUeyY'
GROUP_1_ID = -1003696980644  
GROUP_2_ID = -1003844822699  

# Fayldan faqat usernamelarni o'qib olish
def load_staff():
    staff_list = []
    try:
        if os.path.exists("staff.txt"):
            with open("staff.txt", "r", encoding="utf-8") as f:
                for line in f:
                    username = line.strip()
                    if username.startswith('@'):
                        staff_list.append(username)
        logging.info(f"Yuklangan xodimlar: {len(staff_list)} ta")
    except Exception as e:
        logging.error(f"Fayl o'qishda xato: {e}")
    
    # Agar fayl bo'sh bo'lsa, xato bermasligi uchun zaxira
    if not staff_list:
        staff_list = ["@Yunusjon1994"]
    return staff_list

# Ma'lumotlarni yuklash
STAFF_LIST = load_staff()
current_index = 0
is_session_active = False
current_staff_username = None

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RENDER WEB SERVER ---
async def handle(request):
    return web.Response(text="KM Bot Usernames mode active!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# --- BOT MANTIQI ---
@dp.message(F.chat.id == GROUP_1_ID)
async def session_handler(message: types.Message):
    global current_index, is_session_active, current_staff_username, STAFF_LIST
    
    raw_text = message.text.strip() if message.text else ""
    msg_text = raw_text.lower()

    # 1. Boshlash: "proyekt"
    if msg_text == "proyekt":
        STAFF_LIST = load_staff() # Ro'yxatni yangilash
        is_session_active = True
        current_staff_username = STAFF_LIST[current_index % len(STAFF_LIST)]
        
        await message.reply(
            f"🚀 <b>Yangi proyekt boshlandi!</b>\n"
            f"Mas'ul: <b>{current_staff_username}</b>", 
            parse_mode="HTML"
        )
        return

    # 2. Tugatish: ✅
    if raw_text and "✅" in raw_text:
        # Harf yoki raqam yo'qligini tekshirish
        has_alphanumeric = bool(re.search(r'[a-zA-Z0-9а-яА-Я]', raw_text))
        if not has_alphanumeric:
            if is_session_active:
                await message.reply(
                    f"🛑 <b>Proyekt yakunlandi.</b>\n"
                    f"Navbat keyingi xodimga o'tdi.", 
                    parse_mode="HTML"
                )
                current_index = (current_index + 1) % len(STAFF_LIST)
                is_session_active = False
                current_staff_username = None
            return

    # 3. Fayllarni o'tkazish
    if is_session_active:
        mention_tag = f"\n\n🎯 <b>Mas'ul:</b> {current_staff_username}"
        try:
            if message.text and msg_text != "proyekt":
                await bot.send_message(
                    chat_id=GROUP_2_ID, 
                    text=message.text + mention_tag, 
                    parse_mode="HTML"
                )
            else:
                await bot.copy_message(
                    chat_id=GROUP_2_ID,
                    from_chat_id=GROUP_1_ID,
                    message_id=message.message_id,
                    caption=(message.caption or "") + mention_tag,
                    parse_mode="HTML"
                )
        except Exception as e:
            logging.error(f"Xato: {e}")

async def main():
    asyncio.create_task(start_web_server())
    while True:
        try:
            await dp.start_polling(bot, skip_updates=True)
        except Exception:
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
