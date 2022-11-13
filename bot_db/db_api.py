"""Отвечает за работу с БД"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .db_config import DB_HOST_NAME, DB_NAME, DB_USER, DB_USER_PASSWORD
from .models import Base, User, Recommendations

db_adress = f'postgresql+psycopg2://{DB_USER}:{DB_USER_PASSWORD}@{DB_HOST_NAME}/{DB_NAME}'

def db_connect(function):

    """Декоратор для соединения с БД"""

    def wrapper(*args, **kwargs):
        engine = create_engine(db_adress)
        Base.metadata.create_all(bind=engine)
        with sessionmaker(bind=engine)() as session:
            return function(*args, **kwargs, session=session)
    return wrapper


@db_connect
def add_user(user:User, session=None):

    """
        Добавляет пользователя user в БД
        :param user - польозватель
    """

    session.add(user)
    session.commit()


@db_connect
def update_user(user_id: int, session=None, **kwargs):
    """
        Изменяет информацию пользователя с id user_id в БД
        :param user_id - id пользователя
    """
    user = session.query(User).get(user_id)
    for key, value in kwargs.items():
        if key == 'birthday_year':
            user.birthday_year = value
        elif key == 'sex':
            user.sex = value
        elif key == 'city':
            user.city = value
        elif key == 'status':
            user.status = value
        else:
            print("Ошибка")

    session.add(user)
    session.commit()

@db_connect
def get_all_recommendations(user_id: int, session=None) -> tuple:

    """Возвращает все рекоммендации пользователя """

    result = session.query(Recommendations).filter(Recommendations.client_vk == user_id).all()
    return tuple(x.suggested_vk for x in result)

@db_connect
def does_user_exist(user_id: int, session=None) -> bool:

    """
    Проверяет пользователя с id user_id на наличие в БД
    :param user_id - id пользователя
    """

    if session.query(User).get(user_id):
        return True
    return False

@db_connect
def add_recommendation(client_id: int, suggested_id: int, session=None):

    """
        Создает запись с информацией о том, что пользователю с id client_id
        рекоммендован пользователь с id suggested_id в БД
        :param client_id - id польозвателя
        :param suggested_id - id рекоммендованного пользователя
    """

    recommendation = Recommendations(
        client_vk=client_id,
        suggested_vk=suggested_id
        )
    session.add(recommendation)
    session.commit()


@db_connect
def is_full_info(user_id: int, session=None) -> bool:

    """Возвращает True, если все поля заполнены. Иначе - False"""

    user = session.query(User).get(user_id)
    if user.birthday_year and user.sex and user.city:
        return True
    return False


@db_connect
def get_user(user_id: User, session=None) -> User:

    """Возвращает пользователя с id user_id"""

    user = session.query(User).get(user_id)
    return user
