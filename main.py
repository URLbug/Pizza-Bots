from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

#заказы, тех. поддержку и о нас

from config import config
from text import text, pizza, roll
from context import Zakaz, Helping
from database import *


assort = []
PRISE = [roll,pizza]
prise = {'data': 1,'type': None}

zakaz_arr = {'adres': None,'sum': 0, 'Nabor': None, 'type': [], 'social': None}

bot = Bot(config['TOKEN'])
dp = Dispatcher(bot,storage=MemoryStorage())

@dp.message_handler(commands=['start'])
async def start(m: types.Message):

    if m.from_user.id not in [i for i in session.query(User.id_user).distinct()]:
        users = User(id_user=m.from_user.id,sums=0,types=None)
        session.add(users)
        session.commit()
        session.close()
    
    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(types.KeyboardButton(text='Главная страница')) 

    await m.reply(text['start'],reply_markup=build)

@dp.message_handler(text='Главная страница')
async def start(m: types.Message):

    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(
        types.KeyboardButton(text='Корзина'),
        types.KeyboardButton(text='Ассортимент'),
        types.KeyboardButton(text='Тех. поддержка'),
        types.KeyboardButton(text='О нас')
    )

    await m.reply(text['home'],reply_markup=build)

@dp.message_handler(text='Корзина')
async def start(m: types.Message):
    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(types.KeyboardButton(text='Главная страница'))
    markup = InlineKeyboardMarkup()
    zakaz_arr['type'] = []
    
    if assort == []:
        await m.reply('Ваша корзина пуста(\nХотите вернуться на Главную Страницу?',reply_markup=build)
    else:
        build.add(types.KeyboardButton(text='Заказать все'))
        for i in assort:
            for j in PRISE:
                if i['type'] == j['id']['type']:
                    TF = {'TF': True, 'Goal': j,'f': "{0}\nМинимальный набор {1} {3}\nМаксимальный набор {2} {3}"}
            if TF['TF']:
                markup.add(
                    types.InlineKeyboardButton(f"{i['sum']}", callback_data="null"),
                    types.InlineKeyboardButton("Заказать", callback_data=f"zakaz:{i['sum']}:{i['type']}")
                )
                
                if len(markup.inline_keyboard) > 1:
                    markup.inline_keyboard.pop(0)
                zakaz_arr['type'].append(i['type'])
                zakaz_arr['sum'] += i['sum']

                await m.answer_photo(TF['Goal']['id']['url_photo'],TF['f'].format(TF['Goal']['id']['name'],TF['Goal']['id']['min'],TF['Goal']['id']['max'],TF['Goal']['id']['RUB']),reply_markup=markup)
        
        await m.reply('Ваша корзина',reply_markup=build)

@dp.callback_query_handler(text_startswith='prev')
async def minus(call: types.CallbackQuery):
    calls = call.data.split(':')
    data = int(calls[1])-1

    if data > 0:
        markup = InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("-", callback_data=f"prev:{data}"),
            types.InlineKeyboardButton(str(data), callback_data="null"),
            types.InlineKeyboardButton("+", callback_data=f"next:{data}"),
            types.InlineKeyboardButton("<", callback_data=f"one:{prise['data']-1}"),
            types.InlineKeyboardButton(str(prise['data']), callback_data="null"),
            types.InlineKeyboardButton(">", callback_data=f"two:{prise['data']-1}"),
            types.InlineKeyboardButton("Заказать", callback_data=f"zakaz:{data}:{prise['type']}"),
            types.InlineKeyboardButton("Добавить в корзину",callback_data=f"dop:{data}:{prise['type']}")
            )
        await call.message.edit_reply_markup(markup)

@dp.callback_query_handler(text_startswith='next')
async def next(call: types.CallbackQuery):
    calls = call.data.split(':')
    data = int(calls[1])+1

    if data > 0:
        markup = InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("-", callback_data=f"prev:{data}"),
            types.InlineKeyboardButton(str(data), callback_data="null"),
            types.InlineKeyboardButton("+", callback_data=f"next:{data}"),
            types.InlineKeyboardButton("<", callback_data=f"one:{prise['data']-1}"),
            types.InlineKeyboardButton(str(prise['data']), callback_data="null"),
            types.InlineKeyboardButton(">", callback_data=f"two:{prise['data']-1}"),
            types.InlineKeyboardButton("Заказать", callback_data=f"zakaz:{data}:{prise['type']}"),
            types.InlineKeyboardButton("Добавить в корзину",callback_data=f"dop:{data}:{prise['type']}")
            )
        await call.message.edit_reply_markup(markup)

@dp.callback_query_handler(text_startswith='dop')
async def dop(call: types.CallbackQuery):

    calls = call.data.split(':')
    data_global = int(calls[1])

    assort.append({'type':calls[2],'sum': data_global})
        
    await call.answer('Ваш заказ успешно добавлен в корзину!')

@dp.callback_query_handler(text_startswith='two')
async def two(call: types.CallbackQuery):
    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(types.KeyboardButton(text='Главная страница'))

    calls = call.data.split(':')
    data = int(calls[1])+1
    prise['data'] = data+1

    if data <= len(PRISE):
        i = PRISE[data]
        prise['type'] = i["id"]['type']  
        f = f"{i['id']['name']}\nМинимальный набор {i['id']['min']} {i['id']['RUB']}\nМаксимальный набор {i['id']['max']} {i['id']['RUB']}"

        markup = InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("-", callback_data=f"prev:1"),
            types.InlineKeyboardButton("1", callback_data="null"),
            types.InlineKeyboardButton("+", callback_data=f"next:1"),
            types.InlineKeyboardButton("<", callback_data=f"one:{data}"),
            types.InlineKeyboardButton(str(data+1), callback_data="null"),
            types.InlineKeyboardButton(">", callback_data=f"two:{data}"),
            types.InlineKeyboardButton("Заказать", callback_data=f"zakaz:1:{i['id']['type']}"),
            types.InlineKeyboardButton("Добавить в корзину", callback_data=f"dop:1:{i['id']['type']}")
        )
        await call.message.answer_photo(i['id']['url_photo'],caption=f,reply_markup=markup)
        await call.message.answer('Ассортимент наших блюд',reply_markup=build)

@dp.callback_query_handler(text_startswith='one')
async def two(call: types.CallbackQuery):
    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(types.KeyboardButton(text='Главная страница'))
    
    calls = call.data.split(':')
    data = int(calls[1])-1
    prise['data'] = data+1

    if data <= len(PRISE) and data+1 > 0:
        i = PRISE[data]
        prise['type'] = i["id"]['type']  
        f = f"{i['id']['name']}\nМинимальный набор {i['id']['min']} {i['id']['RUB']}\nМаксимальный набор {i['id']['max']} {i['id']['RUB']}"

        markup = InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("-", callback_data=f"prev:1"),
            types.InlineKeyboardButton("1", callback_data="null"),
            types.InlineKeyboardButton("+", callback_data=f"next:1"),
            types.InlineKeyboardButton("<", callback_data=f"one:{data}"),
            types.InlineKeyboardButton(str(data+1), callback_data="null"),
            types.InlineKeyboardButton(">", callback_data=f"two:{data}"),
            types.InlineKeyboardButton("Заказать", callback_data=f"zakaz:1:{i['id']['type']}"),
            types.InlineKeyboardButton("Добавить в корзину", callback_data=f"dop:1:{i['id']['type']}")
        )
        await call.message.answer_photo(i['id']['url_photo'],caption=f,reply_markup=markup)
        await call.message.answer('Ассортимент наших блюд',reply_markup=build)

@dp.callback_query_handler(text_startswith='zakaz', state=None)
async def zakaz(call: types.CallbackQuery, state: FSMContext):
    calls = call.data.split(':')
    zakaz_arr['type'] = [calls[2]]
    zakaz_arr['sum'] = int(calls[1])

    build = ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton(text='Минимальный набор'),
        types.KeyboardButton(text='Максимальный набор')
    )

    await call.message.answer('Укажите какой вы хотите заказать набор',reply_markup=build)
    await Zakaz.why.set()

@dp.message_handler(state=Zakaz.why)
async def zakaz_2(m: types.Message, state: FSMContext):
    zakaz_arr['Nabor'] = m.text
    sums = 0
    if m.text == 'Минимальный набор':
        for j in PRISE:
            if j['id']['type'] in zakaz_arr['type']:
                sums += j['id']['min']
    else:
        for j in PRISE:
            if j['id']['type'] in zakaz_arr['type']:
                sums += j['id']['min']
    zakaz_arr['sum'] *= sums
    await m.reply('Отлично! Теперь напишите где Вы проживаете')
    await Zakaz.next()

@dp.message_handler(state=Zakaz.what)
async def zakaz_3(m: types.Message, state: FSMContext):
    zakaz_arr['adres'] = m.text

    build = ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton(text='ДА!'),
        types.KeyboardButton(text='НЕТ!')
    )

    await m.reply(f'Отлично! Ваш заказ на сумму {zakaz_arr["sum"]} RUB почти готов\nХотите продолжить?',reply_markup=build)
    await Zakaz.next()

@dp.message_handler(state=Zakaz.nexts)
async def zakaz_4(m: types.Message, state: FSMContext):
    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(types.KeyboardButton(text='Главная страница')) 

    if m.text == 'ДА!':
        await m.reply('Отлично! Напишите Ваш мобильный телефон или Вашу соц. сеть через которую вам будет удобнее связаться')
        await Zakaz.next()
    else:
        await m.reply('Хорошо(.Мы будем ожидать вашего заказа с нетерпением!',reply_markup=build)
        await state.finish()

@dp.message_handler(state=Zakaz.phone)
async def zakaz_5(m: types.Message, state: FSMContext):
    zakaz_arr['social'] = m.text

    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(types.KeyboardButton(text='Главная страница')) 

    await m.reply('Ура! Ваш заказ успешно отправлен менеджеру.\nТеперь ожидайте Ваш заказ',reply_markup=build)
    await state.finish()
    
@dp.message_handler(text='Ассортимент')
async def assorts(m: types.Message):
    f = f"{roll['id']['name']}\nМинимальный набор {roll['id']['min']} {roll['id']['RUB']}\nМаксимальный набор {roll['id']['max']} {roll['id']['RUB']}"

    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(types.KeyboardButton(text='Главная страница'))

    markup = InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("-", callback_data=f"prev:1"),
        types.InlineKeyboardButton("1", callback_data="null"),
        types.InlineKeyboardButton("+", callback_data=f"next:1"),
        types.InlineKeyboardButton("<", callback_data=f"one:0"),
        types.InlineKeyboardButton("1", callback_data="null"),
        types.InlineKeyboardButton(">", callback_data=f"two:0"),
        types.InlineKeyboardButton("Заказать", callback_data=f"zakaz:1:{roll['id']['type']}"),
        types.InlineKeyboardButton("Добавить в корзину", callback_data=f"dop:1:{roll['id']['type']}")
    )
    
    prise['type'] = roll['id']['type']
    await m.answer_photo(roll['id']['url_photo'],f,reply_markup=markup)
    
    await m.answer('Ассортимент наших блюд',reply_markup=build)

@dp.message_handler(text='Заказать все',state=None)
async def zakaz_all(m: types.Message, state: FSMContext):
    zakaz_arr['type'] = zakaz_arr['type']
    zakaz_arr['sum'] = int(zakaz_arr['sum'])

    build = ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton(text='Минимальный набор'),
        types.KeyboardButton(text='Максимальный набор')
    )

    await m.answer('Укажите какой вы хотите заказать набор',reply_markup=build)
    await Zakaz.why.set()

@dp.message_handler(text='Тех. поддержка')
async def helping(m: types.Message):
    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(types.KeyboardButton(text='Помощь'),types.KeyboardButton(text='Главная страница'))

    await m.reply('Если Вы хотите связатся с нами то нажмите на Помощь',reply_markup=build)

@dp.message_handler(text='Помощь',state=None)
async def helping_2(m: types.Message, state=FSMContext):
    await m.reply('Напишите ваш телефон или ваш соц.сеть при помощи которой с Вами можно лего связаться')
    await Helping.why.set()

@dp.message_handler(state=Helping.why)
async def helping_2(m: types.Message, state=FSMContext):
    phone = m.text

    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(types.KeyboardButton(text='Главная страница'))

    await m.reply('Отлично! Ваша заявка принята.\nДождитесь пока с Вами свяжутся',reply_markup=build)
    await state.finish()

@dp.message_handler(text='О нас')
async def our(m: types.Message):
    build = ReplyKeyboardMarkup(resize_keyboard=True)
    build.add(types.KeyboardButton(text='Главная страница'))

    await m.reply('Этот бот сделан для демонстрации того что умеет автор.\nЕсли вы хотите заказать подобного или другого бота то профиль автора тут -> @Hider030',reply_markup=build)

if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True)