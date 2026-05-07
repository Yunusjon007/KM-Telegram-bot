import logging
import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web

# --- KONFIGURATSIYA ---
API_TOKEN = '8695645149:AAGBV002oQ2hHBEBrV3YkXGNisLOhcpUeyY'
GROUP_1_ID = -1003696980644  # KM 1-guruh
GROUP_2_ID = -1003844822699  # KM 2-guruh

# Xodimlar ro'yxati (To'g'ridan-to'g'ri kod ichida)
STAFF_LIST = [
    "@Shoxrux_5557",
    "@eldorchik24",
    "@OYBEK_88_00",
    "@Doston0111"
]

current_index = 0
is_session_active = False
current_staff_username = None

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RENDER WEB SERVER (UYG'OQ TUTISH UCHUN) ---
async def handle(request):
    return web.Response(text="KM Bot User-List mode is active!")

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
    global current_index, is_session_active, current_staff_username
    
    # Xabar matnini olish va bo'shliqlardan tozalash
    raw_text = message.text.strip() if message.text else ""
    msg_text = raw_text.lower()

    # 1. Sessiyani boshlash: "proyekt"
    if msg_text == "proyekt":
        is_session_active = True
        current_staff_username = STAFF_LIST[current_index % len(STAFF_LIST)]
        await message.reply(
            f"🚀 <b>Yangi proyekt boshlandi!</b>\n"
            f"Mas'ul xodim: <b>{current_staff_username}</b>", 
            parse_mode="HTML"
        )
        return

    # 2. Sessiyani tugatish: ✅ (bitta yoki bir nechta)
    # RegEx: xabar ichida ✅ borligini va hech qanday harf/raqam yo'qligini tekshiradi
    if raw_text and "✅" in raw_text:
        # Harf yoki raqam borligini qidirish
        has_alphanumeric = bool(re.search(r'[a-zA-Z0-9а-яА-Я]', raw_text))
        
        if not has_alphanumeric: # Faqat emoji bo'lsa
            if is_session_active:
                await message.reply(
                    f"🛑 <b>Proyekt yakunlandi.</b>\n"
                    f"Mas'ul: <b>{current_staff_username}</b> edi.\n"
                    f"Navbat keyingi xodimga o'tdi.", 
                    parse_mode="HTML"
                )
                # Navbatni keyingi xodimga o'tkazish
                current_index = (current_index + 1) % len(STAFF_LIST)
                is_session_active = False
                current_staff_username = None
            return

    # 3. Fayllarni o'tkazish (Faqat sessiya ochiq bo'lsa)
    if is_session_active:
        # Mas'ul xodimni @username orqali otmetka qilish
        mention_tag = f"\n\n🎯 <b>Mas'ul:</b> {current_staff_username}"
        
        try:
            # Agar xabar faqat matn bo'lsa
            if message.text and msg_text != "proyekt":
                await bot.send_message(
                    chat_id=GROUP_2_ID, 
                    text=message.text + mention_tag, 
                    parse_mode="HTML"
                )
            # Rasm, video yoki hujjat (caption) bo'lsa
            else:
                await bot.copy_message(
                    chat_id=GROUP_2_ID,
                    from_chat_id=GROUP_1_ID,
                    message_id=message.message_id,
                    caption=(message.caption or "") + mention_tag,
                    parse_mode="HTML"
                )
        except Exception as e:
            logging.error(f"Xato yuz berdi: {e}")

# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    # Render o'chib qolmasligi uchun web server
    asyncio.create_task(start_web_server())
    
    # Botni yurgizish
    while True:
        try:
            logging.info("🚀 KM Bot ishga tushdi...")
            await dp.start_polling(bot, skip_updates=True)
        except Exception as e:
            logging.error(f"⚠️ Uzilish: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
