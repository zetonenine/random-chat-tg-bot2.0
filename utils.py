from aiogram.dispatcher.filters.state import State, StatesGroup


class TestStates(StatesGroup):

    chat_process = State()


if __name__ == '__main__':
    print(TestStates.all())