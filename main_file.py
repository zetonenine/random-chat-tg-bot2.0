
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
# import redis


logging.basicConfig(level=logging.INFO)

bot = Bot(token='1233194283:AAEltBBA7sqZ7HPo5Gxef5fALXiqhyRwBqk')

dp = Dispatcher(bot, storage=RedisStorage2(host='ec2-108-128-98-183.eu-west-1.compute.amazonaws.com', port=28589, password='p9fc88e56bed344d5f58352463c019a889910e9cf0b122bb4cfd70977c0f49d18'))
# dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# r = redis.Redis(db=5)


@dp.message_handler(state=None, commands='start')
async def starting(message: types.Message):
    await message.answer('Привет!')


@dp.message_handler(content_types=['text'])
async def hey(message: types.Message):
    await message.answer(message.text)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)

