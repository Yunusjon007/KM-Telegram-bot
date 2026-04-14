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

# Xodimlarning ID raqamlari (Lichkaga xabar borishi uchun)
# Har bir xodim botga kamida bir marta /start bosgan bo'lishi shart!
STAFF_DATA = [
    {"name": "@medprotarget_admin", "id": 123456789}, # IDni to'g'irlang
    {"name": "@dr_radiologist_valiyev", "id": 987654321}, # IDni to'g'irlang
    {"name": "@Yunusjon1994", "id": 510495201}
]

current_index = 0
is_session_active = False
current_staff = None

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RENDER UCHUN WEB SERVER (DUMMY) ---
async def handle(request):
    return web.Response(text="KM Bot is running 24/7 with 1/0 mode!")

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
    
    # Xabar matnini tekshirish
    text = message.text.strip() if message.text else ""

    # 1. Boshlash (Faqat 1 yuborilganda)
    if text == "1":
        is_session_active = True
        current_staff = STAFF_DATA[current_index]
        await message.reply(
            f"🚀 <b>Sessiya boshlandi!</b>\n"
            f"Mas'ul xodim: <b>{current_staff['name']}</b>\n\n"
            f"Hamma yuborilgan fayllar shu xodimga biriktiriladi.", 
            parse_mode="HTML"
        )
        return

    # 2. Tugatish (Faqat 0 yuborilganda)
    if text == "0":
        if is_session_active:
            await message.reply(
                f"🛑 <b>Sessiya tugadi.</b>\n"
                f"Vazifalar <b>{current_staff['name']}</b> ga yuborildi.\n"
                f"Navbat keyingi xodimga o'tdi.", 
                parse_mode="HTML"
            )
            # Navbatni keyingi xodimga o'tkazish
            current_index = (current_index + 1) % len(STAFF_DATA)
            is_session_active = False
            current_staff = None
        else:
            await message.reply("Hozir faol sessiya yo'q. Boshlash uchun <b>1</b> yuboring.", parse_mode="HTML")
        return

    # 3. Fayllarni o'tkazish (Faqat sessiya ochiq bo'lsa)
    if is_session_active:
        caption_text = f"\n\n🎯 <b>Mas'ul:</b> {current_staff['name']}"
        try:
            # 2-guruhga nusxalash
            await bot.copy_message(
                chat_id=GROUP_2_ID,
                from_chat_id=GROUP_1_ID,
                message_id=message.message_id,
                caption=(message.caption or "") + caption_text if (message.caption or message.text) else caption_text,
                parse_mode="HTML"
            )
            
            # Xodimning shaxsiyiga bildirishnoma yuborish
            try:
                await bot.send_message(
                    chat_id=current_staff['id'],
                    text=f"🔔 <b>Yangi vazifa!</b>\nSizga KM 1-guruhda yangi topshiriq biriktirildi. Guruhni tekshiring.",
                    parse_mode="HTML"
                )
            except Exception:
                # Agar xodim botga /start bosmagan bo'lsa xato bermaydi
                pass

        except Exception as e:
            logging.error(f"Xabar yuborishda xatolik: {e}")

# --- ISHGA TUSHIRISH ---
async def main():
    # Web serverni fonda yurgizamiz
    asyncio.create_task(start_web_server())
    
    # Botni uzilishlarsiz yurgizamiz
    while True:
        try:
            logging.info("🚀 Bot Renderda ishga tushdi!")
            await dp.start_polling(bot, skip_updates=True)
        except Exception as e:
            logging.error(f"⚠️ Xatolik yuz berdi: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
