import logging
import functools
import contextlib
from inspect import signature

from sqlalchemy import create_engine, Column, Integer, String, Boolean, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

log = logging.getLogger(__name__)

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

    def __init__(
            self,
            user_id: int
    ):
        self.user_id = user_id


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
                session.query(Connects).filter(Connects.user_id == user_id).update({Connects.partner_user_id: free})
                session.query(Connects).filter(Connects.user_id == free).update({Connects.partner_user_id: user_id})
            except:
                free = None

        return free

    @staticmethod
    def disconnect_users(user_id):
        with create_session() as session:
            free = session.query(Connects).filter(Connects.user_id == user_id).first().partner_user_id
            session.query(Connects).filter(Connects.user_id == user_id).delete()
            try:
                session.query(Connects).filter(Connects.user_id == free).delete()
            except:
                None
            # добавление кол-ва законченных диалогов
            # user = session.query(Users).filter(Users.user_id == user_id).first()
            # par_user = session.query(Users).filter(Users.user_id == free).first()
            # user.showing += 1
            # par_user.showing += 1

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
    def get_partner_user_id(user_id):
        with create_session() as session:
            user_id = session.query(Connects).filter(Connects.user_id == user_id).first().partner_user_id
        return user_id

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
