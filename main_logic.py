import logging
import random
import asyncio

from messages import MESSAGES
from utils import BotStates, ChatState, EditorMode, ModeratorMode, ActiveState, BanState
from adapter import DataInterface
from models import initdb
from celery import Celery

app = Celery('main', broker='redis://:@localhost:6379/1')

log = logging.getLogger(name='main.py')

db = DataInterface()

LOGIN = 'admin'
PASSWORD = 'password'


def add_user(user_id):
    if not db.check_user(user_id):
        db.add_user(user_id)
    return


async def find_user(user_id):
    partner_id = db.add_connects2(user_id)
    return partner_id


def get_partner_id(user_id):
    partner_id = db.get_partner_user_id(user_id)
    return partner_id


async def connect_users(user_id, partner_user_id):
    db.start_room_chat2(user_id, partner_user_id)


async def stop_searching_partner(user_id):
    partner_id = db.stop_searching2(user_id)
    return partner_id


async def stop_room_chat(user_id, partner_user_id):
    db.stop_room_chat2(user_id, partner_user_id)


async def check_partner_appearance(user_id, time):
    partner_id = get_partner_id(user_id)
    if partner_id is not None:
        return
    else:
        if time < 8:
            await asyncio.sleep(time)
            return await check_partner_appearance(user_id, time + 3)
        else:
            await stop_searching_partner(user_id)
            return 'undefined'


async def start_room_chat(user_id):
    partner_id = await find_user(user_id)
    if partner_id:
        await connect_users(user_id, partner_id)
        log.info(f'Users connects: {user_id} and {partner_id}')
        return partner_id
    else:
        partner_id = await check_partner_appearance(user_id, 3)
        if not partner_id:
            log.info(f"User {user_id} didn't find partner")
        return partner_id


async def send_report(user_id, partner_id, reason, messages):
    if reason == 'rude':
        db.send_report(user_id, partner_id, reason, messages)
    elif reason == 'not_english':
        db.send_report(user_id, partner_id, reason, messages)


def remove_partner_id(user_id):
    pass


async def get_tg_banner():
    return db.get_banner()


