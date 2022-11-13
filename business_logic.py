"""Действия бота"""
from datetime import datetime
from bot_db import db_api, models
from message_templates import get_user_birthday_year, \
    get_user_city,get_user_sex, get_profile_update, \
        get_after_update, get_hello, get_cities_list, \
            get_recommended_page, FIND_MESSAGE
import utils

UNDEFINED_COMMAND = {'answer': 'Не понял :(', 'keyboard':{}, 'attachment':''}
UNDEFINED_DATE = {'answer': 'Не может такого быть!', 'keyboard':{}, 'attachment':''}
UNDEFINED_CITY = {'answer': 'Не нашел такого города :(', 'keyboard':{}, 'attachment':''}

SET_BIRTHDAY = 1
SET_SEX = 2
SET_CITY = 3
SELECT_CITY = 4



NEXT = 'qwertyuiop[]asdfghjklzxcvbnm,ytiy;;frd'



def action(user_id: int, message: str) -> dict:

    """
    Обрабатывает сообщение message пользователя с id user_id.
    Возвращает словарь с полями answer и keyboard
    """
    if db_api.does_user_exist(user_id=user_id):
        return existing_user_action(user_id=user_id, message=message)
    return register_new_user(user_id=user_id)

def existing_user_action(user_id: int, message: str) -> dict:

    """Действия с существующими пользователями"""

    if db_api.is_full_info(user_id=user_id):
        if message == FIND_MESSAGE:
            return get_recommendation(user_id)
        if message == NEXT:
            return get_after_update()
        return UNDEFINED_COMMAND
    return update_user_profile(user_id=user_id, message=message)

def update_user_profile(user_id: int, message: str) -> dict:

    """Дозапрашивает и обрабатывает у пользователя с id user_id недостающую информацию"""

    user = db_api.get_user(user_id=user_id)
    if user.status in (SET_SEX, SET_BIRTHDAY, SET_CITY, SELECT_CITY):
        return check_user_params(user_id=user_id, status=user.status, message=message)
    if not user.sex:
        db_api.update_user(user_id=user_id, status=SET_SEX)
        return get_user_sex()
    if not user.birthday_year:
        db_api.update_user(user_id=user_id, status=SET_BIRTHDAY)
        return get_user_birthday_year()
    if not user.city:
        db_api.update_user(user_id=user_id, status=SET_CITY)
        return get_user_city()

def check_user_params(user_id: int, status:int, message: str) -> dict:

    """Передает изменения в обработчики"""

    if status == SET_SEX:
        return set_sex(user_id=user_id, message=message)
    if status == SET_BIRTHDAY:
        return set_birthday(user_id=user_id, message=message)
    if status == SET_CITY:
        return try_set_city(user_id=user_id, message=message)
    if status == SELECT_CITY:
        return set_city(user_id=user_id, message=message)

def set_sex(user_id: int, message:str) -> dict:

    """Устанавливает пол пользователя"""

    if message in ("Я парень", "Я девушка"):
        data = {
            'sex': 2 if message == "Я парень" else 1
        }
        return set_user_info(user_id=user_id, data=data)
    return UNDEFINED_COMMAND

def set_birthday(user_id: int, message: str) -> dict:

    """Устанавливает год рождения пользователя"""

    try:
        value = int(message)
    except ValueError:
        return UNDEFINED_COMMAND
    if value > datetime.now().year or value < 1900:
        return UNDEFINED_DATE
    data = {
        'birthday_year': value
    }
    return set_user_info(user_id=user_id, data=data)

def try_set_city(user_id: int, message:str) -> dict:

    """
    Пытается установить город пользователя.
    Если он не один, то возвращает меню выбора
    """

    cities = utils.city_search(message)
    if len(cities) == 0:
        return UNDEFINED_CITY
    if len(cities) == 1:
        data = {
            'city': cities[0]['id']
        }
        return set_user_info(user_id=user_id, data=data)
    db_api.update_user(user_id=user_id, status=SELECT_CITY)
    return get_cities_list(cities=cities)

def set_city(user_id: int, message:str) -> dict:

    """Устанавливает id города пользователя из списка"""

    #Слова dante и termo с концов id используются, чтобы не спутать id с сообщением
    if message[:5] == 'dante' and message [-5:] == 'termo':
        city_id = message[5:-5]
        data = {
            'city': city_id
        }
        return set_user_info(user_id=user_id, data=data)

def set_user_info(user_id: int, data: dict) -> dict:

    """Изменяет информацию, переданную пользователем"""

    data ['status'] = 0
    db_api.update_user(user_id=user_id, **data)
    return existing_user_action(user_id=user_id, message=NEXT)

def get_recommendation(user_id : int) -> dict:

    """Выдает пользователю предложения для знакомств"""
    user = db_api.get_user(user_id=user_id)
    user_age = datetime.now().year - user.birthday_year
    req = {
        'age_from': user_age - 3,
        'age_to': user_age + 3,
        'sex': 1 if user.sex == 2 else 2,
        'city_id': user.city,
        'offset': 0
        }
    prev_recommendations = db_api.get_all_recommendations(user_id=user_id)
    recommendation = utils.find_recommendation(
        req=req,
        prev_recommendations=prev_recommendations
        )
    db_api.add_recommendation(client_id=user_id, suggested_id=recommendation['id'])
    return get_recommended_page(data=recommendation)

def register_new_user(user_id: int) -> dict:

    """Создает профиль пользователя"""

    profile_info = utils.parse_profile(user_id)
    user = models.User(
        vk_id=profile_info['vk_id'],
        birthday_year=profile_info['birthday_year'],
        sex=profile_info['sex'],
        city=profile_info['city']
    )
    db_api.add_user(user)
    if db_api.is_full_info(user_id=user_id):
        return get_hello(profile_info['name'])

    return get_profile_update(profile_info["name"])
