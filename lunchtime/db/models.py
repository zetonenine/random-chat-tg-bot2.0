import os
import contextlib
import datetime
from typing import Optional, List

from sqlalchemy import create_engine, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import desc

from lunchtime.utils.exceptions import UserAlreadyBanned

# db - с контейнером, localhost - локально

# path = os.environ.get('SQL_ALCHEMY_PATH')
path = "postgresql+psycopg2://tgbot:tgbot@localhost:5432/tgbot"
engine = create_engine(path)
metadata = MetaData(bind=engine)
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=engine)

ACTIVE_USER = 'active'
BANNED_USER = 'banned'


def initdb():
    Base.metadata.create_all(bind=engine)


@contextlib.contextmanager
def create_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    status = Column(String, default=ACTIVE_USER)

    report = relationship('Report', secondary='users_reports_relation', back_populates="user")
    ban = relationship('Ban', uselist=False, backref="user")
    prev_ban = relationship('PrevBan', secondary='users_prev_bans_relation', back_populates="user")

    def __init__(
            self,
            user_id: int,
    ):
        self.user_id = user_id


class Report(Base):
    __tablename__ = 'report'

    id = Column(Integer, primary_key=True)
    user_by = Column(Integer)
    reason = Column(String)
    message = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.datetime.now())

    user = relationship('User', secondary="users_reports_relation", back_populates="report")

    def __init__(
            self,
            user_by: int,
            message: str,
            reason: Optional[str] = None,
            user=[]  # type: List[User]
    ):
        self.user = user
        self.user_by = user_by
        self.reason = reason
        self.message = message


class UsersReportsRelation(Base):
    __tablename__ = 'users_reports_relation'

    id = Column(Integer, primary_key=True)
    users_id = Column(Integer(), ForeignKey('user.id'), nullable=False)
    reports_id = Column(Integer(), ForeignKey('report.id'), nullable=False)


class Ban(Base):
    __tablename__ = 'ban'

    id = Column(Integer, primary_key=True)
    reason = Column(String)
    message = Column(String, nullable=False)
    ban_date = Column(DateTime, default=datetime.datetime.today())
    # moderator_name = Column(String)
    unban_date = Column(DateTime)

    user_id = Column(Integer, ForeignKey(User.user_id), unique=True)

    def __init__(
            self,
            reason: str,
            message: str,
            # moderator_name: str,
            unban_date: Optional[DateTime],
            user: Optional[User]
    ):
        self.reason = reason
        self.message = message,
        # self.moderator_name = moderator_name,
        self.unban_date = unban_date
        self.user = user


class PrevBan(Base):
    __tablename__ = 'prev_ban'

    id = Column(Integer, primary_key=True)
    reason = Column(String)
    message = Column(String, nullable=False)

    user = relationship('User', secondary='users_prev_bans_relation', back_populates="prev_ban")

    def __init__(
            self,
            reason: str,
            message: str,
    ):
        self.reason = reason
        self.message = message


class UsersPrevBansRelation(Base):
    __tablename__ = 'users_prev_bans_relation'

    id = Column(Integer, primary_key=True)
    users_id = Column(Integer(), ForeignKey('user.id'), nullable=False)
    prev_ban_id = Column(Integer(), ForeignKey('prev_ban.id'), nullable=False)


class UsersBanListRelation(Base):
    __tablename__ = 'users_bans_relation'

    id = Column(Integer, primary_key=True)
    users_id = Column(Integer(), ForeignKey('user.id'), nullable=False)
    bans_id = Column(Integer(), ForeignKey('ban.id'), nullable=False)


class Commercial(Base):

    __tablename__ = 'commercial'

    id = Column(Integer, primary_key=True)
    text = Column(String)

    def __init__(self, text):
        self.text = text


class Roles(Base):

    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Посмотреть как спрятать данные
    role = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)

    def __init__(
            self,
            login: str,
            password: str,
            role: str,
            user_id: str
    ):
        self.login = login
        self.password = password
        self.role = role
        self.user_id = user_id


class Database:

    def __init__(self):
        self.session = Session()

    @staticmethod
    def count_users_row():
        with create_session() as session:
            result = session.query(User).count()
        return result

    @staticmethod
    def add_user_to_users(user_id):
        with create_session() as session:
            user = User(user_id=user_id)
            result = session.add(user)
        return result

    @staticmethod
    def user_exists(user_id):
        with create_session() as session:
            result = session.query(User).filter(User.user_id == user_id).first() is not None
        return result

    @staticmethod
    def add_user_to_connects(user_id):
        with create_session() as session:
            connect = Connects(user_id=user_id)
            res = session.add(connect)
        return res


    @staticmethod
    def connect_users(user_id):
        with create_session() as session:
            try:
                free = session.query(Connects).filter(
                    Connects.user_id != user_id,
                    Connects.partner_user_id == None
                ).first().user_id

                # убрать эти запроса возвращая только partner_id для кэша
                session.query(Connects).filter(Connects.user_id == user_id).update({Connects.partner_user_id: free})
                session.query(Connects).filter(Connects.user_id == free).update({Connects.partner_user_id: user_id})

            except:
                free = None

        return free

    @staticmethod
    def remove_user_from_connects(user_id):
        with create_session() as session:
            res = session.query(Connects).filter(Connects.user_id == user_id).delete()
        return res

    @staticmethod
    def get_random_text_from_commercial():
        import random
        with create_session() as session:
            banners = session.query(Commercial.text).all()
        return random.choice(banners)[0] if banners else ''

    @staticmethod
    def get_role_by_login(login):
        with create_session() as session:
            data = session.query(Roles.login, Roles.password, Roles.role, Roles.user_id).filter(Roles.login == login).all()
        return data

    @staticmethod
    def show_commercial():
        with create_session() as session:
            q = session.query(Commercial.id, Commercial.text).all()
            res = {id: text for id, text in q}
        return res

    @staticmethod
    def add_new_commercial(text):
        with create_session() as session:
            comm = Commercial(text=text)
            res = session.add(comm)
        return res

    @staticmethod
    def del_commercial(comm_id):
        with create_session() as session:
            res = session.query(Commercial).filter(Commercial.id == comm_id).delete()
        return res

    @staticmethod
    def insert_into_Roles(login, password, role, user_id):
        with create_session() as session:
            role = Roles(login, password, role, user_id)
            session.add(role)
        return

    @staticmethod
    def remove_from_Roles(login):
        with create_session() as session:
            role = session.query(Role).filter(Role.login == login).delete()
        return role

    @staticmethod
    def get_roles_from_Roles(user_id):
        with create_session() as session:
            roles = session.query(Roles.id, Roles.login, Roles.role).filter(Roles.user_id != user_id).all()
        return roles

    @staticmethod
    def del_role_from_Roles(role_id):
        with create_session() as session:
            res = session.query(Roles).filter(Roles.id == role_id).delete()
        return res

    @staticmethod
    def get_role_login_by_user_id(user_id):
        with create_session() as session:
            role = session.query(Roles.login).filter(Roles.user_id == user_id).first()
        return role

    @staticmethod
    def get_users_order_by_amount_reports():
        with create_session() as session:
            res = session.query(User.id, User.reports_amount, User.reports).order_by(User.reports_amount.desc()).limit(5)
        return res

    @staticmethod
    def insert_report_into_Reports(attrs):
        with create_session() as session:
            if attrs['report_id']:
                report = session.query(Report).filter(Report.id == attrs['report_id']).first()
                report.reason = attrs['reason']
                session.merge(report)
                return report.message
            else:
                user = session.query(User).filter(User.user_id==attrs['user_id']).first()
                report = Report(
                    user=[user],
                    user_by=attrs['user_by'],
                    message=attrs['message']
                )
                session.add(report)
                session.flush()
                return report.id

    @staticmethod
    def get_report_by_id(report_id):
        with create_session() as session:
            q = session.query(Report).filter(Report.id == report_id).first()
            res = [q.user, q.user[0].user_id, q.reason, q.message]
        return res

    @staticmethod
    def get_last_report_order_by_date():
        with create_session() as session:
            report = session.query(Report).order_by(desc(Report.date)).first()
            if not report:
                return
            result = report.id, report.reason, report.message, report.date
        return result

    @staticmethod
    def insert_into_Ban(user, user_id, reason, message, terms, report_id):
        """ Добавляет новый объект Ban, удаляет все объекты Report связанные с данным пользователем """
        with create_session() as session:
            q = session.query(Ban).filter(Ban.user_id == user_id).first()
            if q:
                raise UserAlreadyBanned
            unban_date = datetime.datetime.today()+datetime.timedelta(days=terms)
            ban = Ban(reason=reason, message=message, unban_date=unban_date, user=user)
            session.add(ban)
            user.status = BANNED_USER
            session.merge(user)
            q = session.query(Report).filter(Report.id == report_id).first()
            reports = q.user[0].report
            for report in reports:
                session.delete(report)
        return

    @staticmethod
    def remove_report_from_Report(report_id):
        with create_session() as session:
            q = session.query(Report).filter(Report.id == report_id).first()
            reports = q.user[0].report
            for report in reports:
                session.delete(report)
        return

    @staticmethod
    def get_login_from_Role(user_id):
        with create_session() as session:
            login = session.query(Roles.login).filter(Roles.user_id == user_id).first()
        return login

    @staticmethod
    def get_bans_order_by_date():
        week_ago = datetime.datetime.today() - datetime.timedelta(days=7)
        with create_session() as session:
            bans = session.query(
                Ban.id,
                Ban.reason,
                Ban.message,
                Ban.ban_date,
            ).order_by(desc(Ban.ban_date)).filter(Ban.ban_date > week_ago).all()
        return bans

    @staticmethod
    def get_ban_by_id_from_Ban(ban_id):
        with create_session() as session:
            ban = session.query(
                Ban.id,
                Ban.reason,
                Ban.message,
                Ban.ban_date,
            ).filter(Ban.id == ban_id).first()
        return ban

    @staticmethod
    def get_ban_by_date_from_Ban(date):
        next_day = datetime.datetime.today() + datetime.timedelta(days=1)
        with create_session() as session:
            ban = session.query(
                Ban.id,
                Ban.reason,
                Ban.message,
                Ban.ban_date,
            ).filter(Ban.ban_date >= date).filter(Ban.ban_date <= next_day).all()
        return ban

    @staticmethod
    def remove_ban_from_Ban(ban_id):
        with create_session() as session:
            q = session.query(Ban).filter(Ban.id == ban_id).first()
            user_id = q.user_id
            session.delete(q)
            user = session.query(User).filter(User.user_id == q.user_id).first()
            user.status = BANNED_USER
            session.merge(user)
        return user_id

    @staticmethod
    def get_unban_date_from_Ban(user_id):
        with create_session() as session:
            date = session.query(Ban.unban_date).filter(Ban.user_id == user_id).first()
            return date
