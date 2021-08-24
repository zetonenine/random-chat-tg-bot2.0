import logging
import random
import asyncio

from aiogram import Bot, Dispatcher, executor, types
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext

from messages import MESSAGES
from utils import BotStates
from adapter import DataInterface
from models import initdb


initdb()

logging.basicConfig(level=logging.INFO)

bot = Bot(token='1147716469:AAGUwpxYo_GZ9oZzYchORHXGbx1hOB82kCg')

dp = Dispatcher(bot, storage=RedisStorage2())
dp.middleware.setup(LoggingMiddleware())

db = DataInterface()

LOGIN = 'admin'
PASSWORD = 'password'


@dp.message_handler(commands=['count'], state='*')
async def count_user(message: types.Message):
    count = db.count_users()
    await message.answer('Число - ' + str(count))


@dp.message_handler(commands=['start'], state='*')
async def start_and_add_user_in_BD(message: types.Message):

    """Начало работы бота и добавление юзера в БД.
    Возможно стоит добавлять в БД на следующих этапах"""

    if not db.check_user(message.from_user.id):
        db.add_user(message.from_user.id)

    await message.answer(MESSAGES['start'])


@dp.message_handler(commands=['help'], state='*')
async def help_message(message: types.Message):
    """Информация о самом боте"""
    await message.answer(MESSAGES['help'])


@dp.message_handler(commands=['howto'], state='*')
async def howto_message(message: types.Message):
    """Отправка информации об эффективном обучении"""
    await message.answer(MESSAGES['howto'])


@dp.message_handler(commands=['get'], state='*')
async def help_message(message: types.Message):
    """Отправка информации об эффективном обучении"""
    await message.answer(MESSAGES['get'])


@dp.message_handler(state=BotStates.chat_process, commands=['find'])
async def wrong_state_command_find_catcher(message: types.Message):
    await message.answer('You already have a conversation. Just send a voice..')

######################################################
# ХЭНДЛЕРЫ ОБРАБОТЧИКИ ЧАТА - СОСТОЯНИЕ chat_process #
######################################################


@dp.message_handler(state='*', commands=['find'])
async def finding(message: types.Message, state: FSMContext):

    """Меняет status юзера на '1' или 'True'.
    Если юзер не будет добавлен в БД ранее
    то нужно вызвать db.add_user"""

    await BotStates.chat_process.set()
    partner_id = db.add_connects2(message.from_user.id)
    await message.answer('Searching..')
    if partner_id:
        db.start_room_chat2(message.from_user.id, partner_id)
        await message.answer(MESSAGES['match_1'], parse_mode='html')
        await bot.send_message(partner_id, MESSAGES['match_2'], parse_mode='html')
    else:
        await check_partner(message.from_user.id, state, 3)


    # await BotStates.chat_process.set()
    # db.add_connects(message.from_user.id)
    # await message.answer('Searching..')
    #
    # partner_id = db.start_room_chat(message.from_user.id)
    # if partner_id is not None:
    #     await message.answer(MESSAGES['match_1'], parse_mode='html')
    #     await bot.send_message(partner_id, MESSAGES['match_2'], parse_mode='html')
    # else:
    #     await check_partner(message.from_user.id, state, 3)


async def check_partner(user_id, state: FSMContext, time):
    partner_id = db.get_partner_user_id(user_id)

    if partner_id is not None:
        return
    else:
        if time > 8:
            await state.reset_state()
            # db.stop_searching(user_id)
            db.stop_searching2(user_id)
            await bot.send_message(user_id, MESSAGES['no_partner_message'])
            return
        else:
            await asyncio.sleep(time)
            await check_partner(user_id, state, time + 3)


@dp.message_handler(content_types=['voice'], state=BotStates.chat_process)
async def voice_messages_sender(message: types.voice):

    """Обработчик войсов, пересылка сообщения если чат установлен, и ответ, если чата нет"""

    partner_id = db.get_partner_user_id(message.from_user.id)
    await bot.send_voice(partner_id, message.voice.file_id)


@dp.message_handler(commands=['stop'], state=BotStates.chat_process)
async def stop_chat(message: types.Message, state: FSMContext):

    """Меняет status на '0' или 'False'.
    Также очищает partner_chatID.
    Как и в функции finding, возможно нужен вызов db.add_user"""

    partner_id = db.get_partner_user_id(message.from_user.id)
    if partner_id is None:
        # db.stop_room_chat(message.from_user.id)
        db.stop_searching2(message.from_user.id)
        await state.reset_state()
        await message.answer(MESSAGES['stop_searching'])
    else:
        await BotStates.stop_chat_process.set()
        await message.answer(MESSAGES['sure_stop_chat'], parse_mode='html')


@dp.message_handler(content_types=types.ContentTypes.ANY, state=BotStates.stop_chat_process)
async def accept_stop(message: types.Message, state: FSMContext):
    if message.text.lower() == 'yep':
        # partner_id = db.stop_room_chat(message.from_user.id)
        partner_id = db.get_partner_user_id(message.from_user.id)
        db.stop_room_chat2(message.from_user.id, partner_id)
        banner = db.get_banner()
        ad = random.randint(1, 2)
        await state.reset_state()
        await state.storage.reset_state(user=partner_id)
        await message.answer(MESSAGES['stop_1'] + (('\n\n' + banner) if banner and ad == 1 else ''))
        await bot.send_message(partner_id, MESSAGES['stop_2'] + (('\n\n' + banner) if banner and ad == 1 else ''))
    else:
        await BotStates.chat_process.set()
        await message.answer(MESSAGES['continue_chat'])


@dp.message_handler(content_types=['text', 'sticker', 'photo', 'video'], state=BotStates.chat_process)
async def messages_chat_catcher(message: types.Message):

    """Если состяние chat_process и тип отправляемых сообщений не войс"""

    if message.text != '/find':
        await message.answer('Record a voice message')


######################
# Editor mode states #
######################


@dp.message_handler(commands=['iwanttologin'], state=None)
async def login(message: types.Message):
    await BotStates.login_process.set()
    await message.answer(MESSAGES['editor_mode'])


@dp.message_handler(content_types=types.ContentTypes.ANY, state=BotStates.login_process)
async def check_login(message: types.Message, state: FSMContext):
    await state.reset_state()
    login, password = message.text.split(' ')
    if login == LOGIN and password == PASSWORD:
        await BotStates.editor_mode.set()
        await message.answer(MESSAGES['log_in_success'])
        await menu_editor(message.from_user.id)
    else:
        await message.answer(MESSAGES['log_in_unsuccess'])


@dp.message_handler(commands=['menu'], state=BotStates.editor_mode)
async def menu_editor(user_id):
    await bot.send_message(user_id, MESSAGES['editor_menu'])


@dp.message_handler(commands=['del_editor_mode'], state=BotStates.editor_mode)
async def show_banners(state: FSMContext):
    await state.reset_state()


@dp.message_handler(commands=['show_banners'], state=BotStates.editor_mode)
async def show_banners(message: types.Message):
    banners = db.show_commercial()
    answer = ''
    for id, text in banners.items():
        answer += f"{id}\n{text}\n\n"
    if answer:
        await message.answer(answer)
    else:
        await message.answer(MESSAGES['empty_banners'])


@dp.message_handler(commands=['add_new_banner'], state=BotStates.editor_mode)
async def add_new_banner(message: types.Message, state: FSMContext):
    await message.answer(MESSAGES['send_new_banner'])
    await BotStates.add_banner_process.set()


@dp.message_handler(content_types=types.ContentTypes.ANY, state=BotStates.add_banner_process)
async def write_banner_to_add(message: types.Message, state: FSMContext):
    await state.reset_state()
    try:
        db.add_new_commercial_text(message.text)
        await message.answer(MESSAGES['banner_was_added'])
    except:
        await message.answer(MESSAGES['banner_was_not_added'])
    await BotStates.editor_mode.set()
    await menu_editor(message.from_user.id)


@dp.message_handler(commands=['del_banner'], state=BotStates.editor_mode)
async def del_banner(message: types.Message, state: FSMContext):
    await message.answer(MESSAGES['choose_banner_to_del'])
    await BotStates.del_banner_process.set()


@dp.message_handler(content_types=types.ContentTypes.ANY, state=BotStates.del_banner_process)
async def choose_banner_to_delete(message: types.Message, state: FSMContext):
    answer = message.text
    await state.reset_state()
    try:
        banner_id = int(answer)
        res = db.del_commercial(banner_id)
        if res:
            await message.answer(MESSAGES["banner_was_delete"] + str(banner_id))
        else:
            await message.answer(MESSAGES["banner_was_not_delete"] + str(banner_id))
    except:
        await message.answer(MESSAGES['error_id'])

    await BotStates.editor_mode.set()
    await menu_editor(message.from_user.id)


@dp.message_handler(commands=['quit'], state=BotStates.editor_mode)
async def stop_editor_mode(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer(MESSAGES['stop_editor_mode'])


@dp.message_handler(content_types=types.ContentTypes.ANY, state=None)
async def messages_catcher(message: types.Message):

    """Проверка на состояние: находится ли юзер в чате с кем-то в данный момент или нет"""

    if message.content_type == 'voice':
        await message.answer('First you need to find chat partner. Click /find to do it')
    else:
        await message.answer('Use commands. For example: /find')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


