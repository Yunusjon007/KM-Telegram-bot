import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web

# --- KONFIGURATSIYA ---
API_TOKEN = '8695645149:AAGBV002oQ2hHBEBrV3YkXGNisLOhcpUeyY'
GROUP_1_ID = -1003696980644  
GROUP_2_ID = -1003844822699  

# Xodimlarning ID raqamlarini @userinfobot orqali aniqlab, bu yerga yozing
STAFF_DATA = [
    {"name": "@medprotarget_admin", "id": 123456789}, # IDni almashtiring
    {"name": "@dr_radiologist_valiyev", "id": 987654321}, # IDni almashtiring
    {"name": "@Yunusjon1994", "id": 510495201} # Sizning ID raqamingiz
]

current_index = 0
is_session_active = False
current_staff = None

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RENDER UCHUN WEB SERVER ---
async def handle(request):
    return web.Response(text="KM Bot is running 24/7!")

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
    text = message.text.lower() if message.text else ""

    # 1. Sessiyani boshlash
    if text == "1":
        is_session_active = True
        current_staff = STAFF_DATA[current_index]
        await message.reply(f"🚀 Sessiya boshlandi!\nMas'ul: <b>{current_staff['name']}</b>", parse_mode="HTML")
        return

    # 2. Sessiyani tugatish
    if text == "0":
        if is_session_active:
            await message.reply(f"🛑 Sessiya tugadi.\nNavbat keyingi xodimga o'tdi.", parse_mode="HTML")
            current_index = (current_index + 1) % len(STAFF_DATA)
            is_session_active = False
            current_staff = None
        return

    # 3. Fayllarni o'tkazish
    if is_session_active:
        caption_text = f"\n\n🎯 <b>Mas'ul:</b> {current_staff['name']}"
        try:
            # Guruhga nusxalash
            await bot.copy_message(
                chat_id=GROUP_2_ID,
                from_chat_id=GROUP_1_ID,
                message_id=message.message_id,
                caption=(message.caption or "") + caption_text if (message.caption or message.text) else caption_text,
                parse_mode="HTML"
            )
            
            # Xodimning lichkasiga xabar yuborish
            try:
                await bot.send_message(
                    chat_id=current_staff['id'],
                    text=f"🔔 <b>Yangi vazifa!</b>\n\nSizga KM 1-guruhdan yangi topshiriq biriktirildi. Uni guruhda tekshiring.",
                    parse_mode="HTML"
                )
            except Exception:
                # Agar xodim botga /start bosmagan bo'lsa, xato bermasligi uchun
                logging.warning(f"{current_staff['name']} botga start bosmagan.")

        except Exception as e:
            logging.error(f"Xatolik: {e}")

# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    # Web serverni fonda yurgizamiz
    asyncio.create_task(start_web_server())
    
    # Botni abadiy siklda yurgizamiz (uzilishlar bo'lmasligi uchun)
    while True:
        try:
            logging.info("🚀 Bot Renderda ishga tushdi!")
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
