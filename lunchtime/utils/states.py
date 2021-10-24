from aiogram.dispatcher.filters.state import State, StatesGroup


class BotStates(StatesGroup):
    login_process = State()


class ChatState(StatesGroup):
    default = State()
    stop_chat_process = State()


class EditorMode(StatesGroup):
    default = State()
    add_banner_process = State()
    del_banner_process = State()
    add_role_process = State()
    del_role_process = State()
    get_ban_process = State()
    get_ban_by_id_process = State()
    get_ban_by_date_process = State()


class ModeratorMode(StatesGroup):
    default = State()
    punishment = State


class ActiveState(StatesGroup):
    default = State()


class BanState(StatesGroup):
    default = State()


if __name__ == '__main__':
    print(BotStates.all())