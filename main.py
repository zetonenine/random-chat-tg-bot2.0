from main_logic import log
import random

from aiogram import Bot, Dispatcher, executor, types
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from celery import Celery

app = Celery('main', broker='redis://:@localhost:6379/1')

from messages import MESSAGES
from lunchtime.utils.states import BotStates, ChatState, EditorMode, ModeratorMode, ActiveState, BanState
from adapter import DataInterface
from models import initdb
from main_logic import remove_report, get_moderator_name, get_oldest_report, ban_user, add_user, stop_room_chat, \
    get_partner_id, send_report, stop_searching_partner, \
    start_room_chat, get_tg_banner, get_bans_list, get_ban_by_id, get_ban_by_date, unban_by_user_id
from lunchtime.utils.exceptions import UserAlreadyBanned


initdb()

# logging.basicConfig(level=logging.INFO)

bot = Bot(token='1147716469:AAGUwpxYo_GZ9oZzYchORHXGbx1hOB82kCg')

dp = Dispatcher(bot, storage=RedisStorage2())
dp.middleware.setup(LoggingMiddleware())

db = DataInterface()

LOGIN = 'admin'
PASSWORD = 'password'
my_user_id = 379096786
try:
    db.add_new_role(LOGIN, PASSWORD, 'Admin', my_user_id)
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

    partner_id = get_partner_id(message.from_user.id)
    log.info(f'User {message.from_user.id} send report to user {partner_id}')
    await stop_room_chat(message.from_user.id, partner_id)
    await ActiveState.default.set()
    await state.storage.set_state(user=partner_id, state=ActiveState.default.state)
    await message.answer(MESSAGES['stop_1'])
    await bot.send_message(partner_id, MESSAGES['stop_2'])
    log.info(f'Users disconnects: {message.from_user.id} and {partner_id}')


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
    # await ActiveState.default.set()
    try:
        login, password = message.text.split(' ')
    except:
        await message.answer('Error')
        await ActiveState.default.set()
    db_login, db_password, db_role, db_user_id = db.login_check(login)

    # Протестировать логику неправильного ввода в модераторский режим

    if login == db_login and password == db_password and message.from_user.id == db_user_id:
        await message.answer(MESSAGES['log_in_success'])
        if db_role == 'Admin':
            await EditorMode.default.set()
            await menu_editor(message.from_user.id)
        elif db_role == 'Moderator':
            await ModeratorMode.default.set()
            await menu_moderator(message.from_user.id)

        attempt = "successful"
    else:
        await message.answer(MESSAGES['log_in_unsuccess'])
        await ActiveState.default.set()
        attempt = "unsuccessful"
    log.info(f'Attempt to log in editor mode was {attempt}. user_id:{message.from_user.id}')


async def menu_editor(user_id):
    await bot.send_message(user_id, MESSAGES['editor_menu'])


@dp.message_handler(commands=['menu'], state=EditorMode)
async def menu_editor_handler(message: types.Message):
    await menu_editor(message.from_user.id)


async def menu_moderator(user_id):
    await bot.send_message(user_id, MESSAGES['moderator_menu'])


@dp.message_handler(commands=['menu'], state=ModeratorMode)
async def menu_moderator_handler(message: types.Message):
    await menu_moderator(message.from_user.id)


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


async def ban_sender(user_id, ban, list=False):
    try:
        if list:
            for i in ban:
                ban_id, reason, message_id, date = i
                btn = InlineKeyboardButton('Подробнее', callback_data=f'bnh.more.{ban_id}')
                inline_kb = InlineKeyboardMarkup().add(btn)
                await bot.send_message(
                    chat_id=user_id,
                    text=f"Ban ID: {ban_id}\n"
                         f"Reason: {reason}\n"
                         f"Date: {date.strftime('%d %b %H:%M:%S')}",
                    reply_markup=inline_kb
                )
        else:
            ban_id, reason, message_id, date = ban
            btn1 = InlineKeyboardButton('Разбанить', callback_data=f'bnh.unban1.{ban_id}')
            btn2 = InlineKeyboardButton('Оставить', callback_data=f'bnh.unban2.{ban_id}')
            inline_kb = InlineKeyboardMarkup().add(btn1, btn2)
            await bot.send_voice(
                chat_id=user_id,
                voice=message_id,
                caption=f"Ban ID: {ban_id}\n"
                        f"Reason: {reason}\n"
                        f"Date: {date.strftime('%d %b %H:%M:%S')}",
                reply_markup=inline_kb
            )
    except:
        await bot.send_message(user_id, 'Что-то пошло не так')


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith('bnh'), state=EditorMode
)
async def ban_handler(callback_query: types.CallbackQuery):
    """

    """
    await callback_query.message.delete_reply_markup()
    user_id = callback_query.from_user.id
    _, type, ban_id = callback_query.data.split('.')
    if type == 'more':
        ban = await get_ban_by_id(ban_id)  # получить объекты которые нужно
        await ban_sender(user_id, ban)

    elif type == 'unban1':
        try:
            await unban_by_user_id(ban_id)
            await bot.send_message(user_id, 'Пользователь разбанен')
        except:
            await bot.send_message(user_id, 'Что-то пошло не так')

    elif type == 'unban2':
        await bot.send_message(user_id, 'Пользователь останется в бане')

    await bot.delete_message(user_id, callback_query.message.message_id)


@dp.message_handler(commands=['last_bans'], state=EditorMode.default)
async def ban_list(message: types.Message, state: FSMContext):
    """

    """
    bans = await get_bans_list()
    await ban_sender(message.from_user.id, bans, True)


@dp.message_handler(commands=['get_ban'], state=EditorMode.default)
async def get_ban(message: types.Message, state: FSMContext):
    """

    """
    inline_btn_1 = InlineKeyboardButton('ID', callback_data=f'byid')
    inline_btn_2 = InlineKeyboardButton('Date', callback_data=f'bydate')
    inline_kb = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
    await bot.send_message(
        message.from_user.id,
        text='По какому атрибуту ищем?',
        reply_markup=inline_kb
    )
    await EditorMode.get_ban_process.set()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('byid'), state=EditorMode.get_ban_process)
async def put_ban_id(callback_query: types.CallbackQuery):
    """

    """
    await EditorMode.get_ban_by_id_process.set()
    await bot.send_message(callback_query.from_user.id, 'Напиши ID:')


@dp.message_handler(content_types=types.ContentTypes.ANY, state=EditorMode.get_ban_by_id_process)
async def ban_by_id_handler(message: types.Message, state: FSMContext):
    """

    """
    await EditorMode.default.set()
    ban_id = message.text
    ban = await get_ban_by_id(ban_id)  # получить объекты которые нужно
    if ban:
        await ban_sender(message.from_user.id, ban)
    elif ban == None:
        await bot.send_message(message.from_user.id, 'Указанный бан не найден')
    else:
        await bot.send_message(message.from_user.id, 'Ошибка при вводе ID')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('bydate'), state=EditorMode.get_ban_process)
async def put_ban_date(callback_query: types.CallbackQuery):
    """

    """
    await EditorMode.get_ban_by_date_process.set()
    await bot.send_message(callback_query.from_user.id, 'Напиши дату в формате 21.09.21:')


@dp.message_handler(content_types=types.ContentTypes.ANY, state=EditorMode.get_ban_by_date_process)
async def ban_by_date_handler(message: types.Message, state: FSMContext):
    """

    """
    await EditorMode.default.set()
    date = message.text
    bans = await get_ban_by_date(date)  # получить объекты которые нужно
    if bans:
        await ban_sender(message.from_user.id, bans, True)
    elif bans == None:
        await bot.send_message(message.from_user.id, 'Указанный бан не найден')
    else:
        await bot.send_message(message.from_user.id, 'Ошибка при вводе даты')


@dp.message_handler(commands=['add_role'], state=EditorMode.default)
async def add_new_role(message: types.Message, state: FSMContext):
    await EditorMode.add_role_process.set()
    await message.answer(MESSAGES['add_new_role'])


@dp.message_handler(content_types=types.ContentTypes.ANY, state=EditorMode.add_role_process)
async def get_info_new_role(message: types.Message, state: FSMContext):
    try:
        login, password, role, user_id = message.text.split(' ')
        db.add_new_role(login, password, role, user_id)
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


@dp.message_handler(commands=['reports'], state=ModeratorMode.default)
async def show_report_handler(message: types.Message):
    await show_report(message.from_user.id)


async def show_report(user_id):
    """ Реализовавть функцию выдачи самого старого репорта
    Логика обращения к БД
    Получение: report_id, reason, message, date

    Выводится:
        Report ID:
        Reason:
        Date:
        voice_message
        Кнопки: Наказать / Пропустить / Отмена
        callback_data: chs.punish.<report_id> / chs.skip.<report_id> / chs.cancel.<report_id>
    """
    result = await get_oldest_report()  # сделать функцию

    if result:
        report_id, reason, message_id, date = result
        msg = await bot.send_voice(
            user_id,
            message_id,
            caption=f"Report ID: {report_id}\n"
                    f"Reason: {reason}\n"
                    f"Date: {date.strftime('%d %b %H:%M:%S')}"
        )

        inline_btn_1 = InlineKeyboardButton('Наказать', callback_data=f'chs.punish.{msg.message_id+1}.{report_id}')
        inline_btn_2 = InlineKeyboardButton('Не наказывать', callback_data=f'chs.nopunish.{msg.message_id+1}.{report_id}')
        inline_btn_3 = InlineKeyboardButton('Пропустить', callback_data=f'chs.skip.{msg.message_id+1}.{report_id}')
        inline_kb = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2, inline_btn_3)
        await bot.send_message(
            user_id,
            text='Что сделать с этим пользователем?',
            reply_markup=inline_kb
        )
    else:
        await bot.send_message(
            user_id,
            text='Пока нет заведённых репортов',
        )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('chs'), state=ModeratorMode)
async def choose_punishment(callback_query: types.CallbackQuery):

    """ Происходит проверка нажатой кнопки
    if punish:
        Activate state ModeratorMode.punishment
        Выводится:
            message: Выбери причину бана
            button: Not english, Rude, Scam, etc.
            callback_data: f'rsn.<last_message_id>/<report_id>/<reason>/'
    elif skip:
        Заглушка
    elif cancel:
        await menu_moderator(message.from_user.id)

     """
    await callback_query.message.delete_reply_markup()
    _, action, msg_id, report_id = callback_query.data.split('.')
    if action == 'punish':
        # await ModeratorMode.punishment.set()
        inline_btn_1 = InlineKeyboardButton('Not English', callback_data=f'rsn.{msg_id}.{report_id}.noeng')
        inline_btn_2 = InlineKeyboardButton('Rude', callback_data=f'rsn.{msg_id}.{report_id}.rude')
        inline_btn_3 = InlineKeyboardButton('Scam', callback_data=f'rsn.{msg_id}.{report_id}.scam')
        inline_btn_4 = InlineKeyboardButton('Other', callback_data=f'rsn.{msg_id}.{report_id}.other')

        inline_kb = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2, inline_btn_3, inline_btn_4)
        await bot.edit_message_text(
            text='Какая причина бана?',
            chat_id=callback_query.from_user.id,
            message_id=msg_id,
            reply_markup=inline_kb
        )
    elif action == 'nopunish':
        # await ModeratorMode.punishment.set()
        await remove_report(report_id)
        await bot.delete_message(callback_query.from_user.id, msg_id)
        await bot.send_message(callback_query.from_user.id, 'Нарушений не обнаружено, репорт удалён')
        await show_report(callback_query.from_user.id)
    elif action == 'skip':
        """ 
        Здесь можно реализовать логику получения репортов паком, и получать каждый через генератор
        Как это было сделано в боте для повторения слов
         """
        await bot.delete_message(callback_query.from_user.id, int(msg_id)-1)
        await bot.delete_message(callback_query.from_user.id, int(msg_id))
        await bot.send_message(callback_query.from_user.id, 'Пока логика не реализована')
        await show_report(callback_query.from_user.id)


@dp.callback_query_handler(
    lambda c: c.data and c.data.startswith('rsn') or c.data.startswith('term'),
    state=ModeratorMode
)
async def punishment_callbacks(callback_query: types.CallbackQuery):
    """ Ловит callback данные от процесса вынесения наказания

    data_type, data = callback_query.data.split('.')
    # data_type: rsn/term,
    # data: ID предыдущего сообщения, данные с предыдщих ответов, например: not_english
    if rsn: # reason
        await bot.delete_message(<chat_id>, data)
        text: Выбери количество дней в бане?
        buttons: 1, 3, 7, 30, 360, forever
        callback_data: f'term.<last_message_id>/<report_id>/<reason>/<days>'

    elif term: # reason
        await bot.delete_message(<chat_id>, data)
        text: Подтвердить наказание: Ban days: <data.days>, Reason: <data.reason>, Moderator: <Moderator.name>
        buttons: Подтвердить
        callback_data: f'pns.<last_message_id>/<report_id>/<reason>/<days>'

     """
    await callback_query.message.delete_reply_markup()
    data_type = callback_query.data.split('.')[0]

    if data_type == 'rsn':
        data_type, msg_id, report_id, reason = callback_query.data.split('.')
        btn_1 = InlineKeyboardButton('1', callback_data=f'term.{msg_id}.{report_id}.{reason}.1')
        btn_2 = InlineKeyboardButton('3', callback_data=f'term.{msg_id}.{report_id}.{reason}.3')
        btn_3 = InlineKeyboardButton('7', callback_data=f'term.{msg_id}.{report_id}.{reason}.7')
        btn_4 = InlineKeyboardButton('30', callback_data=f'term.{msg_id}.{report_id}.{reason}.30')
        btn_5 = InlineKeyboardButton('360', callback_data=f'term.{msg_id}.{report_id}.{reason}.360')
        btn_6 = InlineKeyboardButton('Forever', callback_data=f'term.{msg_id}.{report_id}.{reason}.forever')

        inline_kb = InlineKeyboardMarkup().add(btn_1, btn_2, btn_3, btn_4, btn_5, btn_6)
        await bot.edit_message_text(
            text='Выбери количество дней в бане?',
            chat_id=callback_query.from_user.id,
            message_id=msg_id,
            reply_markup=inline_kb
        )

    elif data_type == 'term':
        moderator = await get_moderator_name(callback_query.from_user.id)

        data_type, msg_id, report_id, reason, term = callback_query.data.split('.')
        btn_1 = InlineKeyboardButton('Подтвердить', callback_data=f'pns.{msg_id}.{report_id}.{reason}.{term}')
        btn_2 = InlineKeyboardButton('Отменить', callback_data=f'pnsnot.{msg_id}.{report_id}.{reason}.{term}')
        inline_kb = InlineKeyboardMarkup().add(btn_1, btn_2)

        await bot.edit_message_text(
            text=f"Наказание:\n"
                 f"Ban days: {term}\n"
                 f"Reason: {reason}\n"
                 f"Moderator: {moderator[0] if moderator else 'None'}",
            chat_id=callback_query.from_user.id,
            message_id=msg_id,
            reply_markup=inline_kb
        )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('pns'), state=ModeratorMode)
async def punishment_confirm(callback_query: types.CallbackQuery):

    """ Иммитация функции которая будет принимать ответ: что делать с пользователем
    Это callback-data который в себе принесёт: report_id, terms (срок бана)

    data_type, data = callback_query.data.split('.')
    if pns: # reason
        role = await get_role(message.from_user.id)
        await ban_user(data.report_id, data.reason, data.days, role)
        и дальше по написанной логике ниже
    """

    await callback_query.message.delete_reply_markup()
    data_type, msg_id, report_id, reason, term = callback_query.data.split('.')

    if data_type == 'pns':
        try:
            reason, user_id = await ban_user(report_id, 10)
            # await state.storage.set_state(user=user_id, state=BanState.default.state)
            patner_id = get_partner_id(user_id)
            if patner_id:
                await state.storage.set_state(user=patner_id, state=Ac.default.state)
                await bot.send_message(partner_id, MESSAGES['stop_2'])
                log.info(f'Users disconnects: {callback_query.from_user.id} and {partner_id}')
            # добавить возможность пользователю со статусом Ban смотреть информацию о правилах использования бота
            await bot.edit_message_text(
                text='Пользователь был забанен',
                chat_id=callback_query.from_user.id,
                message_id=msg_id
            )
            # добавить в BanState
            await bot.send_message(user_id, f'Вам ограничено использование бота на {term} дней по причине: {reason}')

        except Exception as ex:
            log.error(f'Не удалось добавить пользователя в Баню: {ex}')
            await bot.send_message(callback_query.from_user.id, 'Не удалось забанить пользователя')

        except UserAlreadyBanned:
            await bot.send_message(partner_id, 'Пользователь уже находится в бане')

    elif data_type == 'pnsnot':
        await bot.delete_message(callback_query.from_user.id, msg_id)
        await bot.send_message(callback_query.from_user.id, 'Наказание отменено')


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