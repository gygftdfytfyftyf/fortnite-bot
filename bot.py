import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "8201805973:AAGZSBTr6rQ2ZKqo-MQyfqPhhgxwULHHo-w"
SHOP_URL = "https://www.fortnite.com/item-shop"
CHAT_ID = -1003733233313  # сюда вставишь id группы

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

users = set()  # сюда сохраняются участники


# Получаем картинку магазина
async def get_shop_image():
    url = "https://fortnite-api.com/v2/shop/br"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data["data"]["image"]


# Кнопка
def keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🛒 Открыть магазин", url=SHOP_URL))
    return kb


# Отправка магазина
async def send_shop(chat_id):
    image = await get_shop_image()
    await bot.send_photo(
        chat_id=chat_id,
        photo=image,
        caption="🔥 Магазин Fortnite обновился!",
        reply_markup=keyboard()
    )


# Сохраняем пользователей
@dp.message_handler()
async def save_user(message: types.Message):
    if message.from_user:
        users.add(message.from_user.id)


# Команда /shop
@dp.message_handler(commands=["shop"])
async def manual_shop(message: types.Message):
    await send_shop(message.chat.id)


# Команда /all
@dp.message_handler(commands=["all"])
async def mention_all(message: types.Message):
    if not users:
        await message.answer("Никого не найдено.")
        return

    mentions = ""
    for user_id in users:
        mentions += f'<a href="tg://user?id={user_id}">👤</a> '

    await message.answer(f"📢 Внимание всем!\n\n{mentions}")


# Авто в 3:00
async def scheduled_shop():
    await send_shop(CHAT_ID)


if __name__ == "__main__":
    scheduler.add_job(scheduled_shop, "cron", hour=3, minute=0)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
