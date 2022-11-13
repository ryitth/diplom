"""Утилиты работы с API ВК"""
from __future__ import annotations

from datetime import datetime
import vk_api
from bot_config import VK_LOGIN, VK_PASSWORD, TWO_FACTOR_AUTHENTICATION

def auth_handler():

    """ При двухфакторной аутентификации вызывается эта функция."""

    # Код двухфакторной аутентификации
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device

def vk_login(function):

    """Декоратор для создания сессии в ВК"""

    def wrapper(*args, **kwargs):
        if TWO_FACTOR_AUTHENTICATION:
            vk_session = vk_api.VkApi(
                login=VK_LOGIN,
                password=VK_PASSWORD,
                auth_handler=auth_handler,
                )
            vk_session.auth(token_only=True)
        else:
            vk_session = vk_api.VkApi(
                login=VK_LOGIN,
                password=VK_PASSWORD
                )
            vk_session.auth()
        return function(*args, **kwargs, vk_session=vk_session)
    return wrapper

def value_or_none(data: dict | None, key: str):

    """
        Если data является словарем и в нем существует ключ key, возвращает значение из словаря.
        Иначе - None.
    """

    if data:
        if key in data:
            return data[key]
    return None

@vk_login
def parse_profile(user_id: int, vk_session=None):

    """Возвращает информацию профиля с id user_id"""

    profile_info =  vk_session.get_api().users.get(
        user_ids=user_id,
        fields='sex, relation, city, bdate, first_name'
        )
    vk_id = profile_info[0]['id']
    city = value_or_none(value_or_none(profile_info[0], 'city'), 'id')
    sex = profile_info[0]['sex']
    first_name = profile_info[0]['first_name']
    bdate = value_or_none(profile_info[0], 'bdate')

    birthday_year = None
    if bdate:
        if len(bdate.split('.')) == 3:
            birthday_year = datetime.strptime(bdate, '%d.%m.%Y').year

    return {
        'vk_id': vk_id,
        'birthday_year': birthday_year,
        'city': city,
        'sex': sex,
        'name': first_name
    }

@vk_login
def city_search(name: str, vk_session=None) -> dict:

    """Возвращает список городов с именем name"""

    cities = vk_session.get_api().database.getCities(q=name, country_id='1')
    choices = []
    for city in cities['items']:
        if city['title'].lower() == name.lower():
            choices.append(city)
    return choices

@vk_login
def get_recommendation_users(req: dict, vk_session=None) -> dict:

    """Выдает список пользователей с подходящими параметрами"""

    sex = req['sex']
    city_id = req['city_id']
    from_age = req['age_from']
    to_age = req['age_to']
    offset = req['offset']
    result = vk_session.get_api().users.search(
        sex=sex,
        city_id=city_id,
        age_from=from_age,
        age_to=to_age,
        count=50,
        sort=0,
        status=6,
        offset=offset,
    )
    return result

@vk_login
def get_recommended_user_photos(vk_id: int, vk_session=None) -> dict:

    """Ищет фотографии пользователя и возвращает словарь с ключомами success и photos"""

    user = vk_session.get_api().users.get(user_ids=vk_id, fields='counters')[0]
    count = user['counters']['photos']
    if count >= 3:
        photos = vk_session.get_api().photos.getAll(
            owner_id=vk_id, count=200
            )
        photos_ids = []
        for photo in photos['items']:
            photos_ids.append(f'{vk_id}_{photo["id"]}')
        photos_info = vk_session.get_api().photos.getById(
            photos=','.join(photos_ids),
            extended=1,
        )
        result_photo_list = []
        for photo in photos_info:
            result_photo_list.append({
                'link': f"photo{photo['owner_id']}_{photo['id']}",
                'popularity': photo['likes']['count'] + photo['comments']['count']
            })
        newlist = sorted(result_photo_list, key=lambda d: d['popularity'], reverse=True)[:3]
        return {'success': True, 'photos': newlist}
    return {'success': False, 'photos': []}

def find_recommendation(req: dict, prev_recommendations: tuple, ) -> dict:

    """Возвращает словарь с данными рекоммендованного пользователя"""

    recommendation_list = get_recommendation_users(req=req)
    photo_check = {'success': False}
    final_recommendaion = None
    for potential_recommendation in recommendation_list['items']:
        if potential_recommendation['is_closed'] or \
            potential_recommendation['id'] in prev_recommendations:
            continue
        photo_check = get_recommended_user_photos(potential_recommendation['id'])
        if photo_check['success']:
            final_recommendaion = potential_recommendation
            break
    if photo_check['success']:
        return {
            'id': final_recommendaion['id'],
            'photos': photo_check['photos'],
            }
    req['offset'] += 50
    return find_recommendation(
        req=req,
        prev_recommendations=prev_recommendations
    )