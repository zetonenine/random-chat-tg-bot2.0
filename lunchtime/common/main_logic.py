import logging
import asyncio
import datetime

from lunchtime.db.adapter import DataInterface
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
        if time < 50:
            await asyncio.sleep(5)
            return await check_partner_appearance(user_id, time + 5)
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
        partner_id = await check_partner_appearance(user_id, 5)
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
    """ Возможно стоит вынести сессиию на этот уровень """

    res = db.get_report(report_id)
    user_obj, user_id, reason, message = res
    db.add_Ban(user_obj[0], user_id, reason, message, terms, report_id)
    return reason, user_id


async def get_tg_banner():
    return db.get_banner()


async def get_bans_list():
    """ Возвращает все баны полученные за последнии 7 дней """
    return db.get_last_bans()


async def get_ban_by_id(ban_id):
    """ Возвращает бан объект по ID """
    try:
        ban_id = int(ban_id)
    except:
        return False
    return db.get_ban_by_id(ban_id)


async def get_ban_by_date(ban_date):
    """ Возвращает бан объект по Date """
    splited_date = ban_date.split('.')
    if not 2 < len(splited_date) < 4:
        return False
    for i in splited_date:
        if len(i) != 2:
            return False
    date = datetime.datetime.strptime(ban_date, '%d.%m.%y')
    return db.get_ban_by_date(date)


async def unban_by_user_id(ban_id):
    """ Удаляет бан по id """
    return db.remove_ban(ban_id)


async def unbanned_date(user_id):
    return db.get_unbanned_date(user_id)
