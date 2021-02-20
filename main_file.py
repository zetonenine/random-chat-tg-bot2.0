
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext

from messages import MESSAGES
from utils import TestStates
from postgresqler import BD


logging.basicConfig(level=logging.INFO)

bot = Bot(token='1147716469:AAGUwpxYo_GZ9oZzYchORHXGbx1hOB82kCg')

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

db = BD()


@dp.message_handler(commands=['start'], state='*')
async def start_and_add_user_in_BD(message: types.Message):

    """Начало работы бота и добавление юзера в БД.
    Возможно стоит добавлять в БД на следующих этапах"""

    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
    # db.redis_add_user(message.from_user.id)
    await message.answer(MESSAGES['start'])


@dp.message_handler(commands=['help'], state='*')
async def help_message(message: types.Message):
    """Информация о самом боте"""
    await message.answer(MESSAGES['help'])


@dp.message_handler(commands=['howto'], state='*')
async def help_message(message: types.Message):
    """Отправка информации об эффективном обучении"""
    await message.answer(MESSAGES['howto'])


@dp.message_handler(commands=['get'], state='*')
async def help_message(message: types.Message):
    """Отправка информации об эффективном обучении"""
    await message.answer(MESSAGES['get'])


@dp.message_handler(state=TestStates.chat_process, commands=['find'])
async def wrong_state_command_find_catcher(message: types.Message):
    await message.answer('You already have a conversation. Just send a voice..')

# ХЭНДЛЕРЫ ОБРАБОТЧИКИ ЧАТА - СОСТОЯНИЕ chat_process


@dp.message_handler(state='*', commands=['find'])
async def finding(message: types.Message, state: FSMContext):

    """Меняет status юзера на '1' или 'True'.
    Если юзер не будет добавлен в БД ранее
    то нужно вызвать db.add_user"""

    db.status_true(message.from_user.id)
    await TestStates.chat_process.set()
    await message.answer('Searching..')
    """Ищем свободного юзера со status'ом = 1. Добавляем юзера в состояние."""

    partner_chatID = db.finding_free_chat(message.from_user.id)
    if partner_chatID is not None:
        await message.answer(MESSAGES['match_1'], parse_mode='html')
        await bot.send_message(partner_chatID, MESSAGES['match_2'], parse_mode='html')


@dp.message_handler(content_types=['voice'], state=TestStates.chat_process)
async def voice_messages_resender(message: types.voice):

    """Обработчик войсов, пересылка сообщения если чат установлен, и ответ, если чата нет"""

    pcID = db.pcID_checker(message.from_user.id)
    await bot.send_voice(pcID, message.voice.file_id)


@dp.message_handler(commands=['stop'], state=TestStates.chat_process)
async def stop_chat(message: types.Message, state: FSMContext):

    """Меняет status на '0' или 'False'.
    Также очищает partner_chatID.
    Как и в функции finding, возможно нужен вызов db.add_user"""

    pcID = db.status_false_and_clear_partner(message.from_user.id)

    await state.reset_state()
    await state.storage.reset_state(user=pcID)
    await message.answer(MESSAGES['stop_1'])
    await bot.send_message(pcID, MESSAGES['stop_2'])


@dp.message_handler(content_types=['text', 'sticker', 'photo', 'video'], state=TestStates.chat_process)
async def messages_chat_catcher(message: types.Message):

    """Если состяние chat_process и тип отправляемых сообщений не войс"""

    if message.text != '/find':
        await message.answer('Record a voice message.')


# ЗДЕСЬ ЗАКАНЧИВАЮТСЯ


@dp.message_handler(state=None, content_types=types.ContentTypes.ANY)
async def messages_catcher(message: types.Message):
    """Проверка на состояние: находится ли юзер в чате с кем-то в данный момент или нет"""

    if message.content_type == 'voice':
        await message.answer('First you need to find chat partner. Click /find to do it')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


