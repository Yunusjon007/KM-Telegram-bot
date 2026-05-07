import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web

# --- KONFIGURATSIYA ---
API_TOKEN = '8695645149:AAGBV002oQ2hHBEBrV3YkXGNisLOhcpUeyY'

# Guruh ID raqamlari
GROUP_1_ID = -1003696980644  # KM 1-guruh
GROUP_2_ID = -1003844822699  # KM 2-guruh

# Xodimlar ro'yxati (IDlarni @userinfobot orqali to'g'irlab oling)
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

# --- RENDER WEB SERVER ---
async def handle(request):
    return web.Response(text="KM Bot 'proyekt' va '✅' rejimida faol!")

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
    
    # Xabar matnini tozalash
    msg_text = message.text.strip().lower() if message.text else ""

    # 1. Sessiyani boshlash ("proyekt" deb yozilganda)
    if msg_text == "proyekt":
        is_session_active = True
        current_staff = STAFF_DATA[current_index]
        await message.reply(
            f"🚀 <b>Yangi proyekt boshlandi!</b>\n"
            f"Mas'ul xodim: <b>{current_staff['name']}</b>\n\n"
            f"Barcha yuborilgan fayllar unga biriktiriladi.", 
            parse_mode="HTML"
        )
        return

    # 2. Sessiyani tugatish (✅ yoki ✅✅✅... yuborilganda)
    # Bu shart xabarda faqat ✅ belgilari borligini tekshiradi
    if msg_text and all(char == '✅' for char in message.text.strip()):
        if is_session_active:
            await message.reply(
                f"🛑 <b>Proyekt yakunlandi.</b>\n"
                f"Mas'ul: <b>{current_staff['name']}</b> edi.\n"
                f"Navbat keyingi xodimga o'tdi.", 
                parse_mode="HTML"
            )
            # Navbatni almashtirish
            current_index = (current_index + 1) % len(STAFF_DATA)
            is_session_active = False
            current_staff = None
        else:
            await message.reply("Hozir faol proyekt yo'q. Boshlash uchun <b>proyekt</b> deb yozing.", parse_mode="HTML")
        return

    # 3. Fayllarni o'tkazish (Sessiya ochiq bo'lsa)
    if is_session_active:
        # Xodimni 2-guruhda otmetka qilish
        mention_tag = f"\n\n🎯 <b>Mas'ul:</b> {current_staff['name']}"
        
        try:
            await bot.copy_message(
                chat_id=GROUP_2_ID,
                from_chat_id=GROUP_1_ID,
                message_id=message.message_id,
                caption=(message.caption or "") + mention_tag if (message.caption or message.text) else mention_tag,
                parse_mode="HTML"
            )
            
            # Xodimning shaxsiyiga bildirishnoma
            try:
                await bot.send_message(
                    chat_id=current_staff['id'],
                    text=f"🔔 <b>Sizga yangi vazifa!</b>\nKM guruhida proyekt biriktirildi.",
                    parse_mode="HTML"
                )
            except Exception:
                pass # Botga start bosilmagan bo'lsa

        except Exception as e:
            logging.error(f"Xatolik: {e}")

# --- ISHGA TUSHIRISH ---
async def main():
    asyncio.create_task(start_web_server())
    while True:
        try:
            logging.info("🚀 Bot Renderda ishga tushdi!")
            await dp.start_polling(bot, skip_updates=True)
        except Exception as e:
            logging.error(f"⚠️ Xatolik: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
