import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web

# --- KONFIGURATSIYA ---
API_TOKEN = '8695645149:AAGBV002oQ2hHBEBrV3YkXGNisLOhcpUeyY'
GROUP_1_ID = -1003696980644  
GROUP_2_ID = -1003844822699  

STAFF_LIST = ["@medprotarget_admin", "@dr_radiologist_valiyev", "@Yunusjon1994"]
current_index = 0
is_session_active = False
current_staff = None

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RENDER UCHUN WEB SERVER ---
async def handle(request):
    return web.Response(text="Bot is running!")

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

    if text == "start":
        is_session_active = True
        current_staff = STAFF_LIST[current_index]
        await message.reply(f"🚀 Sessiya boshlandi! Mas'ul: <b>{current_staff}</b>", parse_mode="HTML")
        return

    if text == "stop":
        if is_session_active:
            await message.reply(f"🛑 Sessiya tugadi. Mas'ul <b>{current_staff}</b> edi.", parse_mode="HTML")
            current_index = (current_index + 1) % len(STAFF_LIST)
            is_session_active = False
            current_staff = None
        return

    if is_session_active:
        caption_text = f"\n\n🎯 <b>Mas'ul:</b> {current_staff}"
        try:
            await bot.copy_message(
                chat_id=GROUP_2_ID,
                from_chat_id=GROUP_1_ID,
                message_id=message.message_id,
                caption=(message.caption or "") + caption_text if (message.caption or message.text) else caption_text,
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Xatolik: {e}")

async def main():
    asyncio.create_task(start_web_server())
    logging.info("🚀 Bot Renderda ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
