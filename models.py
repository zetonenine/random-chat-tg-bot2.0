import logging
import functools
import contextlib
import datetime
from inspect import signature

from sqlalchemy import create_engine, Column, Integer, String, Boolean, MetaData, JSON, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

log = logging.getLogger("models.py")

# db - с контейнером, localhost - локально
path = "postgresql+psycopg2://tgbot:tgbot@localhost:5432/tgbot"
engine = create_engine(path, echo=True)
metadata = MetaData(bind=engine)
Base = declarative_base(metadata=metadata)
Session = sessionmaker(bind=engine)


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


# def provide_session(func):
#
#     func_params = signature(func).parameters
#     try:
#         session_args_idx = tuple(func_params).index("session")
#     except ValueError:
#         raise ValueError(f"Function {func..qualname} has no session argument") from None
#     del func_params
#
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         if "session" in kwargs or session_args_idx < len(args):
#             return func(*args, **kwargs)
#         else:
#             with create_session() as session:
#                 return func(*args, session=session, **kwargs)
#
#     return wrapper


class Users(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    showing = Column(Integer, default=0)

    reports = relationship('Reports', secondary='users_reports_relation')
    # ban_id = relationship('BlackList', back_populates='blacklists')

    def __init__(
            self,
            user_id: int
    ):
        self.user_id = user_id


class Reports(Base):

    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    reason = Column(String, nullable=False)
    messages = Column(String, nullable=False)

    users = relationship('Users', secondary='users_reports_relation')

    def __init__(
            self,
            reason: str,
            messages: str
    ):
        self.reason = reason
        self.messages = messages


class UsersReportsRelation(Base):
    __tablename__ = 'users_reports_relation'

    id = Column(Integer, primary_key=True)
    users_id = Column(Integer(), ForeignKey('users.id'), nullable=False)
    reports_id = Column(Integer(), ForeignKey('reports.id'), nullable=False)


class BlackList(Base):
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True)
    reason = Column(Integer, default=0)
    date_ban = Column(DateTime, nullable=False)
    date_unban = Column(DateTime, nullable=False)

    # user_id = Column(Integer(), ForeignKey('users.id'))

    def __init__(
            self,
            reason: int
    ):
        self.reason = reason


# убрать эту таблицу оставив только кэш
class Connects(Base):

    __tablename__ = 'connects'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    partner_user_id = Column(Integer, unique=True, nullable=True)

    def __init__(
            self,
            user_id: int
    ):
        self.user_id = user_id


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

    def __init__(
            self,
            login: str,
            password: str,
            role: str,
    ):
        self.login = login
        self.password = password
        self.role = role


class Database:

    def __init__(self):
        initdb()
        self.session = Session()

    @staticmethod
    def count_users_row():
        with create_session() as session:
            result = session.query(Users).count()
        return result

    @staticmethod
    def add_user_to_users(user_id):
        with create_session() as session:
            user = Users(user_id=user_id)
            result = session.add(user)
        return result

    @staticmethod
    def user_exists(user_id):
        with create_session() as session:
            result = session.query(Users).filter(Users.user_id == user_id).first() is not None
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
    def disconnect_users(user_id):
        with create_session() as session:
            free = session.query(Connects).filter(Connects.user_id == user_id).first().partner_user_id

            # убрать эти запроса возвращая только partner_id для кэша
            session.query(Connects).filter(Connects.user_id == user_id).delete()
            try:
                session.query(Connects).filter(Connects.user_id == free).delete()
            except:
                None

        return free

    @staticmethod
    def insert_report_to_Reports(user_id, reason, messages):
        with create_session() as session:
            report = Reports(user_id=user_id, reason=reason, messages=messages)

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
            data = session.query(Roles.login, Roles.password, Roles.role).filter(Roles.login == login).all()
        return data[0]

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
    def del_commercial(id):
        with create_session() as session:
            res = session.query(Commercial).filter(Commercial.id == id).delete()
        return res

    @staticmethod
    def insert_into_Roles(login, password, role):
        with create_session() as session:
            role = Roles(login, password, role)
            session.add(role)
        return

    @staticmethod
    def get_roles_from_Roles():
        with create_session() as session:
            roles = session.query(Roles.id, Roles.login, Roles.role).filter(Roles.role != 'Admin').all()
        return roles

    @staticmethod
    def del_role_from_Roles(role_id):
        with create_session() as session:
            res = session.query(Roles).filter(Roles.id == role_id).delete()
        return res

    @staticmethod
    def get_users_order_by_amount_reports():
        with create_session() as session:
            res = session.query(Users.id, Users.reports_amount, Users.reports).order_by(Users.reports_amount.desc()).limit(5)
        return res

    @staticmethod
    def get_reports_by_ids(reports_id):
        with create_session() as session:
            res = []
            for i in reports_id:
                q = session.query(Reports.reason, Reports.messages).filter(Reports.id == i).first()
                res.append(q[0])
        return res

    @staticmethod
    def insert_into_BlackList(user_id, reason):
        with create_session() as session:
            ban = BlackList(reason=reason)
            user = session.query(Users).filter(Users.user_id == user_id).first()[0]
            ban.user_id = user
            session.add(ban)
        return

    @staticmethod
    def del_row_from_BlackList(user_id):
        with create_session() as session:
            user = session.query(Users).filter(Users.user_id == user_id).first()[0]
        return
