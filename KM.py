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

STAFF_DATA = [
    {"name": "@medprotarget_admin", "id": 123456789}, 
    {"name": "@dr_radiologist_valiyev", "id": 987654321},
    {"name": "@Yunusjon1994", "id": 510495201}
]

current_index = 0
is_session_active = False
current_staff = None

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RENDER WEB SERVER (DUMMY) ---
async def handle(request):
    return web.Response(text="KM Bot is fully operational!")

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
    global current_index, is_session_active, current_staff
    
    raw_text = message.text.strip() if message.text else ""
    msg_text = raw_text.lower()

    # 1. Sessiyani boshlash: "proyekt"
    if msg_text == "proyekt":
        is_session_active = True
        current_staff = STAFF_DATA[current_index]
        await message.reply(
            f"🚀 <b>Yangi proyekt boshlandi!</b>\n"
            f"Mas'ul xodim: <b>{current_staff['name']}</b>", 
            parse_mode="HTML"
        )
        return

    # 2. Sessiyani tugatish: Alohida xabarda ✅ kelganda
    # Bu shart xabar ichida ✅ borligini va hech qanday harf/raqam yo'qligini tekshiradi
    if raw_text and "✅" in raw_text:
        # Harf va raqamlarni qidiramiz
        has_alphanumeric = bool(re.search(r'[a-zA-Z0-9а-яА-Я]', raw_text))
        
        if not has_alphanumeric: # Agar harf/raqam bo'lmasa, demak bu faqat emoji xabari
            if is_session_active:
                await message.reply(
                    f"🛑 <b>Proyekt yakunlandi.</b>\n"
                    f"Mas'ul: <b>{current_staff['name']}</b> edi.\n"
                    f"Navbat keyingi xodimga o'tdi.", 
                    parse_mode="HTML"
                )
                current_index = (current_index + 1) % len(STAFF_DATA)
                is_session_active = False
                current_staff = None
            return

    # 3. Fayllarni o'tkazish (Faqat sessiya ochiq bo'lsa)
    if is_session_active:
        mention_tag = f"\n\n🎯 <b>Mas'ul:</b> {current_staff['name']}"
        try:
            # Agar xabar faqat matn bo'lsa (proyekt so'zi emas)
            if message.text and msg_text != "proyekt":
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
            
            # Xodimning shaxsiyiga bildirishnoma
            try:
                await bot.send_message(chat_id=current_staff['id'], text="🔔 Yangi vazifa biriktirildi!")
            except:
                pass

        except Exception as e:
            logging.error(f"Xato: {e}")

# --- ISHGA TUSHIRISH ---
async def main():
    asyncio.create_task(start_web_server())
    while True:
        try:
            logging.info("🚀 Bot Renderda ishlamoqda...")
            await dp.start_polling(bot, skip_updates=True)
        except Exception as e:
            logging.error(f"⚠️ Xatolik: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
