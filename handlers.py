import types
from aiogram import Router,F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import dbWorker
from aiogram.fsm.state import StatesGroup, State
import matcher
import json
import asyncio
r = Router()
db = dbWorker.DB()


@r.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("lorem ipsum dolor sit amet")


@r.message(Command("/menu"))
async def listMenu():
    pass

