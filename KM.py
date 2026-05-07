import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web

# --- KONFIGURATSIYA ---
API_TOKEN = '8695645149:AAGBV002oQ2hHBEBrV3YkXGNisLOhcpUeyY'

# Guruh ID raqamlari
GROUP_1_ID = -1003696980644  # KM 1-guruh (Asosiy)
GROUP_2_ID = -1003844822699  # KM 2-guruh (Natija)

# Xodimlar ro'yxati
# DIQQAT: Xodimlar botga bir marta /start bosishi shart, aks holda lichkaga xabar bormaydi.
STAFF_DATA = [
    {"name": "@medprotarget_admin", "id": 123456789},  # Haqiqiy ID raqamni yozing
    {"name": "@dr_radiologist_valiyev", "id": 987654321}, # Haqiqiy ID raqamni yozing
    {"name": "@Yunusjon1994", "id": 510495201}          # Sizning ID raqamingiz
]

current_index = 0
is_session_active = False
current_staff = None

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- RENDER WEB SERVER (UYG'OQ TUTISH UCHUN) ---
async def handle(request):
    return web.Response(text="KM Bot is running 24/7 with 1/0 logic!")

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
    
    # Faqat matnli buyruqlarni tekshiramiz (1 yoki 0)
    msg_text = message.text.strip() if message.text else ""

    # 1 yuborilganda - Boshlash
    if msg_text == "1":
        is_session_active = True
        current_staff = STAFF_DATA[current_index]
        await message.reply(
            f"🚀 <b>Sessiya boshlandi!</b>\n"
            f"Mas'ul xodim: <b>{current_staff['name']}</b>\n\n"
            f"Barcha fayllar shu xodimga biriktiriladi.", 
            parse_mode="HTML"
        )
        return

    # 0 yuborilganda - Tugatish
    if msg_text == "0":
        if is_session_active:
            await message.reply(
                f"🛑 <b>Sessiya tugadi.</b>\n"
                f"Mas'ul: <b>{current_staff['name']}</b> edi.\n"
                f"Navbat keyingi xodimga o'tdi.", 
                parse_mode="HTML"
            )
            # Navbatni keyingi xodimga surish
            current_index = (current_index + 1) % len(STAFF_DATA)
            is_session_active = False
            current_staff = None
        else:
            await message.reply("Hozir faol sessiya yo'q. Boshlash uchun <b>1</b> yuboring.", parse_mode="HTML")
        return

    # Sessiya ochiq bo'lsa, xabarlarni o'tkazish
    if is_session_active:
        # Xodimni ko'k yozuvda otmetka qilish
        mention_tag = f"\n\n🎯 <b>Mas'ul:</b> {current_staff['name']}"
        
        try:
            # 2-guruhga nusxalash
            await bot.copy_message(
                chat_id=GROUP_2_ID,
                from_chat_id=GROUP_1_ID,
                message_id=message.message_id,
                # Caption bo'lsa qo'shadi, bo'lmasa matnga otmetkani yopishtiradi
                caption=(message.caption or "") + mention_tag if (message.caption or message.text) else mention_tag,
                parse_mode="HTML"
            )
            
            # Xodimning lichkasiga bildirishnoma yuborish
            try:
                await bot.send_message(
                    chat_id=current_staff['id'],
                    text=f"🔔 <b>Yangi vazifa!</b>\nKM 1-guruhda sizga vazifa biriktirildi. Uni guruhda tekshiring.",
                    parse_mode="HTML"
                )
            except Exception:
                # Agar xodim botga start bosmagan bo'lsa, xato bermaydi
                pass

        except Exception as e:
            logging.error(f"Xabar yuborishda xatolik: {e}")

# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    # Web serverni fonda ishga tushiramiz
    asyncio.create_task(start_web_server())
    
    # Botni abadiy siklda yurgizamiz
    while True:
        try:
            logging.info("🚀 Bot Renderda faol...")
            await dp.start_polling(bot, skip_updates=True)
        except Exception as e:
            logging.error(f"⚠️ Uzilish: {e}")
            await asyncio.sleep(5) # Xatolik bo'lsa 5 soniya kutib qayta urinadi

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
