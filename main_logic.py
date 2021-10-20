import logging
import random
import asyncio

from messages import MESSAGES
from utils import BotStates, ChatState, EditorMode, ModeratorMode, ActiveState, BanState
from adapter import DataInterface
from models import initdb, create_session
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


async def send_report(user_by=None, message=None, report_id=None, reason=None):
    attrs = {}
    attrs['report_id'] = report_id if report_id else ''
    attrs['reason'] = reason if reason else ''
    attrs['user_id'] = get_partner_id(user_by) if user_by else ''
    attrs['user_by'] = user_by if user_by else ''
    attrs['message'] = message if message else ''

    return db.add_report(attrs)


def remove_partner_id(user_id):
    pass


async def get_role(user_id):
    return db.get_login_name_by_user_id(user_id)


async def get_oldest_report():
    """ Возвращает самый старый по date репорт """
    return db.get_last_report_order_by_date()


async def remove_report(report_id):
    """ Удаляет репорт по id """
    return db.remove_Report(report_id)


async def get_moderator_name(user_id):
    """ Возвращает имя модератор по user_id """
    return db.get_login_from_role(user_id)


async def ban_user(report_id, terms):
    # with create_session():
    """ Возможно стоит вынести сессиию на этот уровень """
    try:
        res = db.get_report(report_id)
        user, user_id, reason, message = res[0][0], res[1], res[2], res[3]
        db.add_Ban(user, reason, message, terms)
        db.remove_Report(report_id)
        return reason, user_id
    except Exception as ex:
        log.error(ex)
        return


async def get_tg_banner():
    return db.get_banner()


