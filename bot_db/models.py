"""Модуль работы с ORM"""

from sqlalchemy import Column, Integer, SmallInteger, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Recommendations(Base):
    """Класс таблицы связи для работы с БД через ORM"""

    __tablename__ = 'recommendations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_vk = Column(Integer, ForeignKey('users.vk_id'), index=True)
    suggested_vk = Column(Integer)


class User(Base):
    """Класс пользователя для работы с БД через ORM"""

    __tablename__ = 'users'
    vk_id = Column(Integer, primary_key=True)
    birthday_year = Column(Integer, nullable=True)
    sex = Column(SmallInteger, nullable=True)
    city = Column(BigInteger, nullable=True)
    status = Column(SmallInteger, default=0)
