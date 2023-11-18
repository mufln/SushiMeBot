import types
from aiogram import Router,F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import dbWorker
from aiogram.fsm.state import StatesGroup, State
import matcher
import json
import asyncio

import namegen

r = Router()
db = dbWorker.DB()


# ---------------STATE_MACHINES---------------
class AddPartition(StatesGroup):
    waitingForName = State()


class EditPartition(StatesGroup):
    waitingForName = State()


class NewPosition(StatesGroup):
    waitingForPartition = State()
    waitingForName = State()
    waitingForPic = State()
    waitingForDescription = State()
    waitingForCost = State()
    waitingForAll = State()


class Buy(StatesGroup):
    waitingForBin = State()
    waitingForAddr = State()


class Address(StatesGroup):
    waitingForAddress = State()
# ---------------END---------------




# ---------------MISC---------------
@r.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    if not message.from_user.id in db.getUsers():
        db.addUser(message.from_user.id)
    await message.answer("lorem ipsum dolor sit amet")
    await state.clear()


@r.message(Command("help_admin"))
async def AdminHelp(message: types.Message, state: FSMContext):
    await message.answer("""
    Разделы
    /listparts - показывает список разделов
    /addpart - добавление нового раздела, напиши /addpart (название) чтобы добавить сразу
    /delpart - показывает меню с разделами, выбрав элемент которого, будет удален  раздел
    /editpart - показывает меню с разделами, позволяет изменить название раздела
    
    Позиции
    /addpos - добавление новой позиции 
    /delpos - удаление позиции
    /listpos - показать позиции
    
    Адрес
    /addaddr - добавить адрес
    /deladdr - удалить адрес
    /listaddr - показать адреса
    """)
    await state.clear()


@r.message(Command("help"))
async def help(message: types.Message, state: FSMContext):
    await message.answer("""Для начала покупки введи /menu
    Чтобы просмотреть корзину, оформить покупку, используй /bin
    """)
# ---------------END---------------




# ---------------PARTITION---------------
@r.message(Command("listparts"))
async def listPartitions(message: types.Message, state: FSMContext):
    msg = "Разделы:\n"+'\n'.join([f"id {i[0]} название {i[1]}" for i in db.getPartitionsWithID()])
    if msg!="Разделы:\n":
        await message.answer(msg)
    else:
        await message.answer("Разделов нет")
    await state.clear()


@r.message(Command("addpart"))
async def addPartitionBasic(message: types.Message, state: FSMContext):
    if len(message.text.split())>1:
        p = matcher.getPartition(message.text).capitalize()
        db.addPartition(p)
        await message.answer(f"Раздел {p.lower()} добавлен")
    else:
        await message.answer(f"Отправь название нового раздела")
        await state.set_state(AddPartition.waitingForName)


@r.message(AddPartition.waitingForName)
async def addPartitionUsingName(message: types.Message, state: FSMContext):
    p = message.text.lower()
    db.addPartition(p)
    await message.answer(f"Раздел {p} добавлен")
    await state.clear()


@r.message(Command("delpart"))
async def delPartitionKB(message: types.Message, state: FSMContext):
    buttons = [[types.InlineKeyboardButton(text=i[1],callback_data=f"DP {i[0]}")]for i in db.getPartitionsWithID()]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    if buttons!=[[]]:
        await message.answer("Выберите раздел для удаления", reply_markup=kb)
    else:
        await message.answer("Разделов нет")
    await state.clear()


@r.callback_query(F.data.startswith("DP"))
async def delPartition(data = types.CallbackQuery, state = FSMContext):
    db.delPartition(int(data.data.split()[1]))
    await data.message.edit_text("Раздел удален")
    await state.clear()

@r.message(Command("editpart"))
async def editPartNameKB(message: types.Message, state: FSMContext):
    buttons = [[types.InlineKeyboardButton(text=i[1], callback_data=f"EP {i[0]}") for i in db.getPartitionsWithID()]]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    if buttons!=[[]]:
        await message.answer("Выберите раздел для изменения", reply_markup=kb)
    else:
        await message.answer("Разделов нет")
    await state.clear()


@r.callback_query(F.data.startswith("EP"))
async def editPartName(data: types.CallbackQuery, state: FSMContext):
    await data.message.edit_text("Отправьте новое название")
    await state.update_data(id=int(data.data.split()[1]))
    await state.set_state(EditPartition.waitingForName)


@r.message(EditPartition.waitingForName)
async def editPartNameWriteName(message:types.Message, state: FSMContext):
    data = await state.get_data()
    db.editPartition(data["id"],message.text.lower())
    await message.answer("Название раздела изменено")
    await state.clear()
#---------------END---------------




# ---------------POSITION---------------
@r.message(Command("addpos"))
async def AddPosBase(message:types.Message, state: FSMContext):
    await message.answer("""Отправьте полную карточку товара, содержащую все данные
    формат:
    1. Прикрепите изображение к сообщению
    2. Текст сообщения:
    Раздел - (число)
    Название - (название)
    Описание - (описание)
    Стоимость - (число)
    """)
    await state.set_state(NewPosition.waitingForAll)


@r.message(NewPosition.waitingForAll)
async def addAll(message:types.Message, state: FSMContext):
    res = matcher.preparePosition(message.caption)
    photos = message.photo
    if any([type(res)==int,type(photos)==None,res[0] not in db.getPartitionsIds()]):
        await message.answer("Неверный формат или раздела не существует")
        # await state.set_state(NewPosition.waitingForName)
        return

    photo_path = f'sushipics/{namegen.genName(str(res[0])+res[1])}.jpg'
    await message.bot.download(file= photos[-1].file_id, destination=photo_path)
    db.addPosition(res[0], res[1], res[2], res[3], photo_path)
    await message.answer("Новая позиция добавлена")
    await state.clear()


@r.message(Command("delpos"))
async def delPosKB(message:types.Message, state: FSMContext):
    buttons = [ [types.InlineKeyboardButton(text=i[2],callback_data=f"DPOS {i[1]}")] for i in db.getPositions()]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите позицию для удаления", reply_markup=kb)


@r.callback_query(F.data.startswith("DPOS"))
async def delPos(data: types.CallbackQuery, state: FSMContext):
    id = int(data.data.split()[1])
    db.delPosition(id)
    await data.message.edit_text("Позиция удалена")
    await state.clear()


@r.message(Command("listpos"))
async def ListPos(message: types.Message, state: FSMContext):
    ids = db.getPositions()
    buttons = [[types.InlineKeyboardButton(text = ids[1], callback_data=f"SHPOS {ids[0]}")] for i in ids]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    if ids!=[]:
        await message.answer("Выберите позицию",reply_markup=kb)
    else:
        await message.answer("Позиций нет")
    await state.clear()


@r.callback_query(F.data.startswith("SHPOS"))
async def DebugShowPos(data: types.CallbackQuery,state:FSMContext):
    id = int(data.data.split()[1])
    await state.clear()

#---------------END---------------




# ---------------ADDRESS---------------
@r.message(Command("addaddr"))
async def addAddrPrep(message:types.Message, state: FSMContext):
    await message.answer("Отправьте адрес, например: Ул. Пушкина д.52 кв.812 ")
    await state.set_state(Address.waitingForAddress)


@r.message(Address.waitingForAddress)
async def addAddress( message:types.Message, state: FSMContext):
    db.addAddress(message.from_user.id, message.text)
    await message.answer("Адрес добавлен")
    await state.clear()


async def addAddressWhileBuying(data:types.CallbackQuery, state: FSMContext):
    db.addAddress(data.message.from_user.id, data.message.text)
    await data.message.answer("Адрес добавлен")
    await setAddr(data, state)
    return


@r.callback_query(F.data.startswith("DADDR"))
async def delAddr(data:types.CallbackQuery, state: FSMContext):
    db.delAddress(int(data.data.split()[1]))
    await data.message.edit_text("Адрес удален")


@r.message(Command("deladdr"))
async def delAddrPrep(message:types.Message, state: FSMContext):
    buttons = [[types.InlineKeyboardButton(text=i[1],callback_data=f"DADDR {i[0]}")]for i in db.getUserAddresses(message.from_user.id)]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выберите адрес для удаления", reply_markup=kb)


@r.message(Command("listaddr"))
async def listAddresses(message: types.Message, state: FSMContext):
    msg = "\n".join([i[1] for i in db.getUserAddresses(message.from_user.id)])
    if msg !="":
        msg = "Ваши адреса для доставки:\n"+msg
        await message.answer(msg)
    else:
        await message.answer("У вас нет ни одного адреса")
#---------------END---------------




# ---------------BUY---------------
# @r.callback_query(F.data.startswith("LMENU"))
@r.message(Command("menu"))
async def listMenu(message:types.Message, state: FSMContext):
    ids = db.getPartitionsWithID()
    buttons = [[types.InlineKeyboardButton(text=i[1],callback_data=f"SPART {i[0]}")] for i in  ids]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    media = types.FSInputFile(f"sushipics/template.jpg")
    await message.answer_photo(photo=media,caption="Выберите категорию", reply_markup=kb)
    data = await state.get_data()
    if not "bin" in data.keys():
        await state.set_state(Buy.waitingForBin)
        await state.update_data(bin=db.getPositionsIdsDict())


@r.callback_query(F.data.startswith("LMENU"))
async def listMenuFromCallback(data:types.CallbackQuery, state: FSMContext):
    await data.message.delete()
    await listMenu(data.message,state)


@r.callback_query(F.data.startswith("SPART"))
async def SelectPosition(data: types.CallbackQuery, state: FSMContext):
    ids = db.getPositionsWithID(int(data.data.split()[1]))
    await state.update_data(ids = ids, part_id=int(data.data.split()[1]))
    buttons = [[types.InlineKeyboardButton(text="Посмотреть разделы",callback_data="LMENU")]]
    buttons += [[types.InlineKeyboardButton(text=a[1], callback_data=f"SPOS {i}")] for i,a in enumerate(ids)]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    media = types.InputMediaPhoto(media =types.FSInputFile(f"sushipics/template.jpg"))
    await data.message.edit_media(media=media)
    await data.message.edit_caption(caption="Выберите позицию", reply_markup=kb)

#ПЕРЕПИСАТЬ КОРОЧЕ, сделать метод prepPosKB(args)
@r.callback_query(F.data.startswith("SPOS"))
async def AddPos(data: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    ids = state_data["ids"]
    bin = state_data["bin"]

    id = int(data.data.split()[1])
    p = id-1 if id-1>=0 else len(ids)-1
    n = id+1 if id+1<len(ids) else 0

    pos = db.getPos(ids[id][0])[0]
    count = bin[pos[0]]
    cost = count*pos[4]

    buttons = ([[types.InlineKeyboardButton(text="<",callback_data=f"SPOS {p}"),
               types.InlineKeyboardButton(text="меню",callback_data=f"SPART {state_data['part_id']}"),
               types.InlineKeyboardButton(text=">",callback_data=f"SPOS {n}")],
               [types.InlineKeyboardButton(text="-",callback_data=f"SUB {id}"),
               types.InlineKeyboardButton(text="+",callback_data=f"ADD {id}")],
               [types.InlineKeyboardButton(text=f"{count}шт: {cost}pуб",callback_data="VOID")],
               [types.InlineKeyboardButton(text="Перейти к оформлению",callback_data="BUY")]])
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    caption = pos[2] + " - " + str(pos[4])+ "р" + "\n" + pos[3]
    media = types.InputMediaPhoto(media= types.FSInputFile(f"sushipics/{namegen.genName(str(pos[1])+pos[2])}.jpg"))

    await data.message.edit_media(media=media)
    await data.message.edit_caption(caption=caption,reply_markup=kb)


@r.callback_query(F.data.startswith("ADD"))
async def ADDPOS(data:types.CallbackQuery, state: FSMContext):
    id = int(data.data.split()[1])
    user_data = await state.get_data()
    bin = user_data["bin"]
    ids = user_data["ids"]
    bin[ids[id][0]]+=1
    user_data.update(bin=bin)
    await AddPos(data,state)


@r.callback_query(F.data.startswith("SUB"))
async def ADDPOS(data:types.CallbackQuery, state: FSMContext):
    id = int(data.data.split()[1])
    user_data = await state.get_data()
    bin = user_data["bin"]
    ids = user_data["ids"]
    bin[ids[id][0]]-=1 if bin[ids[id][0]]>0 else 0
    user_data.update(bin=bin)
    await AddPos(data,state)


@r.callback_query(F.data.startswith("BUY"))
async def setAddr(data:types.CallbackQuery,state:FSMContext):
    addresses = db.getUserAddresses(data.message.chat.id)
    if addresses == []:
        await addAddressWhileBuying(data=data,state=state)
        return
    buttons = [[types.InlineKeyboardButton(text=f"{i[1]}",callback_data=f"ABUY {i[0]}")] for i in addresses]
    buttons += [[types.InlineKeyboardButton(text="меню",callback_data="LMENU")]]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    user_data = await state.get_data()
    bin = user_data["bin"]
    poses = db.getPositionsNamesDict()
    msg = ""
    total=0
    order = ""
    for n,a in bin.items():
        if a==0:
            continue
        cost = poses[n][1]*a
        total += cost
        msg += f"{poses[n][0]} - {a}шт: {cost}руб.\n"
        order += f"{poses[n][0]} - {a}шт:\n"
    msg += (f"Итого: {total}руб.\n")
    msg += "Выберите адрес, куда доставить заказ"
    order += f"{total}руб."
    media = types.InputMediaPhoto(media = types.FSInputFile("sushipics/template.jpg"))
    await state.update_data(order = order)
    await data.message.edit_media(media=media)
    await data.message.edit_caption(caption=msg, reply_markup=kb)


@r.callback_query(F.data.startswith("ABUY"))
async def acceptOrder(data: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    address = db.getAddressByID(int(data.data.split()[1]))[0]
    staff = db.getStaff()
    await data.message.edit_caption(caption="Заказ принят")
    await data.bot.send_message(staff[0][0],text = user_data["order"]+"\n\n"+address)
