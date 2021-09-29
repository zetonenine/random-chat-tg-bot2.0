from main_logic import log
import random
import asyncio

from aiogram import Bot, Dispatcher, executor, types
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from celery import Celery

app = Celery('main', broker='redis://:@localhost:6379/1')

from messages import MESSAGES
from utils import BotStates, ChatState, EditorMode, ModeratorMode, ActiveState, BanState
from adapter import DataInterface
from models import initdb
from main_logic import add_user, find_user, stop_room_chat, send_report, get_partner_id, send_report, check_partner_appearance, stop_searching_partner, start_room_chat, get_tg_banner


initdb()

# logging.basicConfig(level=logging.INFO)

bot = Bot(token='1147716469:AAGUwpxYo_GZ9oZzYchORHXGbx1hOB82kCg')

dp = Dispatcher(bot, storage=RedisStorage2())
dp.middleware.setup(LoggingMiddleware())

db = DataInterface()

LOGIN = 'admin'
PASSWORD = 'password'
try:
    db.add_new_role(LOGIN, PASSWORD, 'Admin')
except:
    None


@app.task
@dp.message_handler(commands=['count'], state=ActiveState)
async def count_user(message: types.Message):
    count = db.count_users()
    await message.answer('Число - ' + str(count))


@app.task
@dp.message_handler(commands=['start'], state=[None, ActiveState, ChatState])
async def start_and_add_user_in_BD(message: types.Message, state: FSMContext):

    """Начало работы бота и добавление юзера в БД.
    Возможно стоит добавлять в БД на следующих этапах"""

    add_user(message.from_user.id)

    await message.answer(MESSAGES['start'])
    await ActiveState.default.set()


@app.task
@dp.message_handler(commands=['help'], state=[ActiveState, ChatState])
async def help_message(message: types.Message):
    """Информация о самом боте"""
    await message.answer(MESSAGES['help'])
    log.info('hello from help')


@app.task
@dp.message_handler(commands=['howto'], state=[ActiveState, ChatState])
async def howto_message(message: types.Message):
    """Отправка информации об эффективном обучении"""
    await message.answer(MESSAGES['howto'])


@app.task
@dp.message_handler(commands=['get'], state=[ActiveState, ChatState])
async def help_message(message: types.Message):
    """Отправка информации об эффективном обучении"""
    await message.answer(MESSAGES['get'])


@dp.message_handler(commands=['find'], state=ChatState)
async def wrong_state_command_find_catcher(message: types.Message):
    await message.answer('You already have a conversation. Just send a voice..')

######################################################
# ХЭНДЛЕРЫ ОБРАБОТЧИКИ ЧАТА - СОСТОЯНИЕ chat_process #
######################################################


@dp.message_handler(commands=['find'], state=ActiveState)
async def finding(message: types.Message, state: FSMContext):

    """Меняет status юзера на '1' или 'True'.
    Если юзер не будет добавлен в БД ранее
    то нужно вызвать db.add_user"""

    await ChatState.default.set()
    await message.answer('Searching..')
    partner_id = await start_room_chat(message.from_user.id)

    if partner_id == 'undefined':
        await bot.send_message(message.from_user.id, MESSAGES['no_partner_message'])
        await ActiveState.default.set()
    elif partner_id:
        await message.answer(MESSAGES['match_1'], parse_mode='html')
        await bot.send_message(partner_id, MESSAGES['match_2'], parse_mode='html')


@dp.message_handler(content_types=['voice'], state=ChatState)
async def voice_messages_sender(message: types.voice):

    """Обработчик войсов, пересылка сообщения если чат установлен, и ответ, если чата нет"""

    partner_id = get_partner_id(message.from_user.id)
    print(message.voice.file_id)
    await bot.send_voice(partner_id, message.voice.file_id)
    log.info(f'User {message.from_user.id} sent voice to user {partner_id}. Voice_id: {message.voice.values["file_id"]}')


@dp.message_handler(commands=['report'], state=ChatState.default)  # ChatMode()
async def report(message: types.Message, state: FSMContext):
    # keyboards.py
    if message.reply_to_message:
        if message.reply_to_message.voice:
            report_id = await send_report(
                message.from_user.id,
                message.reply_to_message.voice.file_id
            )
            inline_btn_1 = InlineKeyboardButton('Оскорбительное поведение', callback_data=f'btn.rude.{report_id}')
            inline_btn_2 = InlineKeyboardButton('Не использует английский язык', callback_data=f'btn.not_english.{report_id}')
            inline_kb = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
            await message.reply("Select the reason for the report", reply_markup=inline_kb)
        else:
            await message.reply('This is not a voice')
    else:
        await message.reply(MESSAGES['report_explain'])


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'), state=ChatState) # ChatMode()
async def report_callback_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    _, reason, report_id = callback_query.data.split('.')
    file_id = await send_report(report_id=report_id, reason=reason)

    # оставлю пока пересылку сообщения в бот
    await bot.send_voice(chat_id=-1001540464961, voice=file_id)
    await bot.send_message(callback_query.from_user.id, MESSAGES['report_accepted'])
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)


@dp.message_handler(commands=['stop'], state=ChatState.default) # ChatMode()
async def stop_chat(message: types.Message, state: FSMContext):

    """Меняет status на '0' или 'False'.
    Также очищает partner_chatID.
    Как и в функции finding, возможно нужен вызов db.add_user"""

    partner_id = get_partner_id(message.from_user.id)
    if partner_id is None:
        await stop_searching_partner(message.from_user.id)
        await ActiveState.default.set()
        await message.answer(MESSAGES['stop_searching'])
    else:
        await ChatState.stop_chat_process.set()
        await message.answer(MESSAGES['sure_stop_chat'], parse_mode='html')


@dp.message_handler(content_types=types.ContentTypes.ANY, state=ChatState.stop_chat_process)
async def accept_stop(message: types.Message, state: FSMContext):
    if message.text.lower() == 'yep':
        partner_id = get_partner_id(message.from_user.id)
        await stop_room_chat(message.from_user.id, partner_id)
        banner = await get_tg_banner()
        ad = random.randint(1, 2)
        await ActiveState.default.set()
        await state.storage.set_state(user=partner_id, state=ActiveState.default.state)
        await message.answer(MESSAGES['stop_1'] + (('\n\n' + banner) if banner and ad == 1 else ''))
        await bot.send_message(partner_id, MESSAGES['stop_2'] + (('\n\n' + banner) if banner and ad == 1 else ''))
        log.info(f'Users disconnects: {message.from_user.id} and {partner_id}')
    else:
        await ChatState.default.set()
        await message.answer(MESSAGES['continue_chat'])


@dp.message_handler(content_types=['text', 'sticker', 'photo', 'video'], state=ChatState.default)
async def messages_chat_catcher(message: types.Message):

    """Если состяние chat_process и тип отправляемых сообщений не войс"""

    if message.text != '/find':
        await message.answer('Record a voice message')


######################
# Editor mode states #
######################


@dp.message_handler(commands=['iwanttologin'], state=ActiveState)  # ActiveState()
async def login(message: types.Message):
    await BotStates.login_process.set()
    await message.answer(MESSAGES['editor_mode'])


@dp.message_handler(content_types=types.ContentTypes.ANY, state=BotStates.login_process)
async def check_login(message: types.Message, state: FSMContext):
    login, password = message.text.split(' ')
    db_login, db_password, db_role = db.login_check(login)
    if login == db_login and password == db_password:
        await message.answer(MESSAGES['log_in_success'])
        if db_role == 'Admin':
            await EditorMode.default.set()
            await menu_editor(message.from_user.id)
        elif db_role == 'Moderator':
            await ModeratorMode.default.set()

        attempt = "successful"
    else:
        await message.answer(MESSAGES['log_in_unsuccess'])
        await ActiveState.default.set()
        attempt = "unsuccessful"
    log.info(f'Attempt to log in editor mode was {attempt}. user_id:{message.from_user.id}')


@dp.message_handler(commands=['menu'], state=EditorMode)
async def menu_editor(user_id):
    await bot.send_message(user_id, MESSAGES['editor_menu'])


@dp.message_handler(commands=['show_banners'], state=EditorMode.default)
async def show_banners(message: types.Message):
    banners = db.show_commercial()
    answer = ''
    for id, text in banners.items():
        answer += f"{id}\n{text}\n\n"
    if answer:
        await message.answer(answer)
    else:
        await message.answer(MESSAGES['empty_banners'])


@dp.message_handler(commands=['add_new_banner'], state=EditorMode.default)
async def add_new_banner(message: types.Message, state: FSMContext):
    await message.answer(MESSAGES['send_new_banner'])
    await EditorMode.add_banner_process.set()


@dp.message_handler(content_types=types.ContentTypes.ANY, state=EditorMode.add_banner_process)
async def write_banner_to_add(message: types.Message, state: FSMContext):
    try:
        db.add_new_commercial_text(message.text)
        await message.answer(MESSAGES['banner_was_added'])
    except:
        await message.answer(MESSAGES['banner_was_not_added'])
    await EditorMode.default.set()
    await menu_editor(message.from_user.id)


@dp.message_handler(commands=['del_banner'], state=EditorMode.default)
async def del_banner(message: types.Message, state: FSMContext):
    await message.answer(MESSAGES['choose_banner_to_del'])
    await EditorMode.del_banner_process.set()


@dp.message_handler(content_types=types.ContentTypes.ANY, state=EditorMode.del_banner_process)
async def choose_banner_to_delete(message: types.Message, state: FSMContext):
    answer = message.text
    try:
        banner_id = int(answer)
        res = db.del_commercial(banner_id)
        if res:
            await message.answer(MESSAGES["banner_was_delete"] + str(banner_id))
        else:
            await message.answer(MESSAGES["banner_was_not_delete"] + str(banner_id))
    except:
        await message.answer(MESSAGES['error_id'])

    await EditorMode.default.set()
    await menu_editor(message.from_user.id)


@dp.message_handler(commands=['add_role'], state=EditorMode.default)
async def add_new_role(message: types.Message, state: FSMContext):
    await EditorMode.add_role_process.set()
    await message.answer(MESSAGES['add_new_role'])


@dp.message_handler(content_types=types.ContentTypes.ANY, state=EditorMode.add_role_process)
async def get_info_new_role(message: types.Message, state: FSMContext):
    login, password, role = message.text.split(' ')
    try:
        db.add_new_role(login, password, role)
        await message.answer(MESSAGES['role_was_added'])
    except:
        await message.answer(MESSAGES['role_wasnt_added'])
    await EditorMode.default.set()
    await menu_editor(message.from_user.id)


@dp.message_handler(commands=['del_role'], state=EditorMode.default)
async def show_roles_to_del(message: types.Message, state: FSMContext):
    query = db.show_roles()
    roles = ''
    for i, j, q in query:
        roles += f"{i}, {j}, {q}\n"
    if roles:
        await message.answer(MESSAGES['choose_role_to_del'] + '\n\n' + roles)
    else:
        await message.answer(MESSAGES['no_roles_to_del'])
    await EditorMode.del_role_process.set()


@dp.message_handler(content_types=types.ContentTypes.ANY, state=EditorMode.del_role_process)
async def del_role(message: types.Message, state: FSMContext):
    try:
        res = db.del_role(message.text)
        if res:
            await message.answer(MESSAGES['role_was_deleted'])
        else:
            await message.answer(MESSAGES['role_wasnt_deleted'])
    except:
        await message.answer(MESSAGES['error_id'])
    await EditorMode.default.set()
    await menu_editor(message.from_user.id)


@dp.message_handler(commands=['menu'], state=ModeratorMode)
async def menu_moderator(user_id):
    await bot.send_message(user_id, MESSAGES['moderator_menu'])


@dp.message_handler(commands=['show_reports_users'], state=ModeratorMode.default)
async def show_reports_users(message: types.Message, state: FSMContext):
    query = db.most_reports_users()
    users = ''
    inline_kb = InlineKeyboardMarkup()
    for i in enumerate(query):
        users += f"{i[0]}. ID: {i[1][0]} - Reports: {i[1][1]}\n"
        inline_kb.add(InlineKeyboardButton(text=f"{i[1][0]}",
                                           callback_data=f"btn{i[1][2]}"))

    await message.reply("Select user to check", reply_markup=inline_kb)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn'), state=ModeratorMode)
async def check_report_callback_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    reports_id = eval(callback_query.data[-1])
    query = db.get_reports_messages(reports_id)
    reports = ''
    inline_kb = InlineKeyboardMarkup()
    for i in enumerate(query):
        reports += f"{i[0]}. Reason: {i[1][0]}\n"
        inline_kb.add(InlineKeyboardButton(text=f"{reports_id[i[0]]}",
                                           callback_data=f"msg{i[1][1]}"))

    await bot.send_message(callback_query.from_user.id, text=MESSAGES['choose_messages_to_check'], reply_markup=inline_kb)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('msg'), state=ModeratorMode)
async def show_messages(callback_query: types.CallbackQuery):
    # await bot.answer_callback_query(callback_query.id)
    messages_id = eval(callback_query.data[3:])
    await bot.send_message(chat_id=callback_query.from_user.id, text=MESSAGES['messages_of_reports'])
    for i in messages_id:
        await bot.send_voice(chat_id=callback_query.from_user.id, voice=i)
    button1 = KeyboardButton('Забанить')
    button2 = KeyboardButton('Оставить')
    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button1, button2)
    await bot.send_message(chat_id=callback_query.from_user.id, text=MESSAGES['choose_punishment'], reply_markup=greet_kb)


@dp.message_handler(commands=['quit'], state=ModeratorMode)
async def stop_editor_mode(message: types.Message, state: FSMContext):
    await ActiveState.default.set()
    await message.answer(MESSAGES['stop_moderator_mode'])


@dp.message_handler(commands=['quit'], state=EditorMode)
async def stop_editor_mode(message: types.Message, state: FSMContext):
    await ActiveState.default.set()
    await message.answer(MESSAGES['stop_editor_mode'])


@dp.message_handler(content_types=types.ContentTypes.ANY, state=EditorMode)
async def messages_catcher_editor(message: types.Message):
    await message.answer('Use commands.')
    await menu_editor(message.from_user.id)


@dp.message_handler(content_types=types.ContentTypes.ANY, state=ModeratorMode)
async def messages_catcher_moderator(message: types.Message):
    await message.answer('Use commands.')
    await menu_moderator(message.from_user.id)


@dp.message_handler(content_types=types.ContentTypes.ANY, state=ActiveState)
async def messages_catcher_no_mode(message: types.Message):

    """Проверка на состояние: находится ли юзер в чате с кем-то в данный момент или нет"""

    if message.content_type == 'voice':
        await message.answer('First you need to find chat partner. Click /find to do it')
    else:
        await message.answer('Use commands. For example: /find')


@dp.message_handler(content_types=types.ContentTypes.ANY, state=BanState)
async def ban_user_message_catcher(message: types.Message, state: FSMContext):
    # логика написания остатка времени до разбана
    time = 'anytime'
    await message.answer(MESSAGES['ban_user_answer'] + time)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)