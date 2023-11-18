import asyncio

from cfg import *
import logging
import sys
import platform
from handlers import r as router
from aiohttp import web

from aiogram.dispatcher.dispatcher import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application


async def on_startup(bot: Bot) -> None:
    await dropWebhook(bot)
    await bot.set_webhook(
        f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}",
        certificate=FSInputFile(SSL_CERT),
        secret_token=WEBHOOK_SECRET,
    )


async def dropWebhook(bot) -> None:
    await bot.delete_webhook()


def prepBot() -> [Bot, Dispatcher]:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.startup.register(dropWebhook) if platform.system() in("Darwin","Windows") else dp.startup.register(on_startup)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    return bot,dp


def main() -> None:
    bot,dp = prepBot()
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=HOST_PORT, port=HOST_IP)


async def main_poll() -> None:
    bot, dp = prepBot()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    if platform.system() in ("Darwin","Windows"):
        asyncio.run(main_poll())
    else:
        main()