from aiogram.dispatcher.filters.state import State, StatesGroup


class BotStates(StatesGroup):
    chat_process = State()
    stop_chat_process = State()
    login_process = State()
    editor_mode = State()
    add_banner_process = State()
    del_banner_process = State()


if __name__ == '__main__':
    print(BotStates.all())