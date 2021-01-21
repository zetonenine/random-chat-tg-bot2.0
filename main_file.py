
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext

from sqlighter import SQLighter
from messages import MESSAGES
from utils import TestStates



logging.basicConfig(level=logging.INFO)

bot = Bot(token='1147716469:AAGUwpxYo_GZ9oZzYchORHXGbx1hOB82kCg')

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


db = SQLighter('tables.db')


@dp.message_handler(commands=['start'], state='*')
async def start_and_add_user_in_BD(message: types.Message):

    """Начало работы бота и добавление юзера в БД.
    Возможно стоит добавлять в БД на следующих этапах"""

    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
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


# ХЭНДЛЕРЫ ОБРАБОТЧИКИ ЧАТА - СОСТОЯНИЕ chat_process


@dp.message_handler(state='*', commands=['find'])
async def finding(message: types.Message, state: FSMContext):

    """Меняет status юзера на '1' или 'True'.
    Если юзер не будет добавлен в БД ранее
    то нужно вызвать db.add_user"""

    # убрать это условие, когда подключится redis.
    if db.pcID_checker(message.from_user.id) == None:
        db.status_true(True, message.from_user.id)
        await TestStates.chat_process.set()
        await message.answer('Searching..')
        """Ищем свободного юзера со status'ом = 1. Добавляем юзера в состояние."""

        partner_chatID = db.finding_free_chat(message.from_user.id, None)
        if partner_chatID is not None:
            await message.answer(MESSAGES['match_1'], parse_mode='html')
            await bot.send_message(partner_chatID, MESSAGES['match_2'], parse_mode='html')

    else:
        await message.answer('You already have a conversation. Just send a voice..')


@dp.message_handler(content_types=['voice'], state=TestStates.chat_process)
async def voice_messages_resender(message: types.voice, state: FSMContext):

    """Обработчик войсов, пересылка сообщения если чат установлен, и ответ, если чата нет"""

    pcID = db.pcID_checker(message.from_user.id)
    await bot.send_voice(pcID, message.voice.file_id)


@dp.message_handler(commands=['stop'], state=TestStates.chat_process)
async def stop_chat(message: types.Message, state: FSMContext):

    """Меняет status на '0' или 'False'.
    Также очищает partner_chatID.
    Как и в функции finding, возможно нужен вызов db.add_user"""

    pcID = db.status_false_and_clear_partner(False, message.from_user.id, None)

    await state.finish()
    await message.answer(MESSAGES['stop_1'])
    await bot.send_message(pcID, MESSAGES['stop_2'])


@dp.message_handler(content_types=['text', 'sticker', 'photo'], state=TestStates.chat_process)
async def messages_chat_catcher(message: types.Message, state: FSMContext):
    pcID = db.pcID_checker(message.from_user.id)

    """Проверка на состояние: находится ли юзер в чате с кем-то в данный момент или нет"""
    # убрать это условие, когда подключится redis.

    if db.pcID_checker(message.from_user.id) != None:
        if message.text != '/find':
            await message.answer('Record a voice message.')
    else:
        await state.finish()
        await messages_catcher(message)


# ЗДЕСЬ ЗАКАНЧИВАЮТСЯ


@dp.message_handler(commands=['check'], state='*')
async def checking(message: types.Message):

    """Проверка на наличие юзера в базе данных"""

    if not db.user_exists(message.from_user.id):
        await message.answer('Вы не в базе')
    else:
        await message.answer('Вы в базе')


@dp.message_handler(commands=['delete'], state='*')
async def deleting(message: types.Message):

    """Удаление юзера из БД"""

    if db.user_exists(message.from_user.id):
        db.user_deleting(message.from_user.id)
        await message.answer('Вы удалены из базы')


@dp.message_handler(state=None, content_types=types.ContentTypes.ANY)
async def messages_catcher(message: types.Message):
    """Проверка на состояние: находится ли юзер в чате с кем-то в данный момент или нет"""

    if message.content_type == 'voice':
        # убрать это условие, когда подключится redis.
        if db.pcID_checker(message.from_user.id) is None:
            await message.answer('Для начала тебе нужно найти собеседника. Чтобы это сделать нажми /find')
        else:
            await TestStates.chat_process.set()
            await voice_messages_resender(message, state=TestStates.chat_process)

    else:
        if db.pcID_checker(message.from_user.id) is None:
            await message.answer('Это классно конечно, но не то. Чтобы найти собеседника, нажми /find')
        else:
            await TestStates.chat_process.set()
            await messages_chat_catcher(message, state=TestStates.chat_process)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


