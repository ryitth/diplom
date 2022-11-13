"""Шаблоны сообщений"""

from vk_api.keyboard import VkKeyboard, VkKeyboardColor

FIND_MESSAGE = "Найди мне половинку!"
find_keyboard = VkKeyboard(one_time=False)
find_keyboard.add_button(FIND_MESSAGE, color=VkKeyboardColor.PRIMARY)

def get_user_birthday_year() -> dict:

    """Создает сообщение для опредления года рождения"""

    keyboard = VkKeyboard.get_empty_keyboard()
    answer = "Скажи мне, пожалуйста, год твоего рождения"
    return {'answer': answer, 'keyboard':keyboard, 'attachment':''}

def get_user_sex() -> dict:

    """Создает сообщение для определения пола"""

    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Я парень", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Я девушка", color=VkKeyboardColor.PRIMARY)
    answer = "Нужно определиться с твоим полом"
    return {'answer': answer, 'keyboard':keyboard.get_keyboard(), 'attachment':''}

def get_user_city() -> dict:

    """Создает сообщение для определения города"""

    keyboard = VkKeyboard.get_empty_keyboard()
    answer = "Из какого ты города?"
    return {'answer': answer, 'keyboard':keyboard, 'attachment':''}

def get_profile_update(name: str) -> dict:

    """Создает сообщение для дозапроса"""

    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Да!', color=VkKeyboardColor.POSITIVE)
    return {
        'answer': f'Привет, {name}!\n' +
        'Для работы нам нужно заполнить небольшую анкету, приступим?',
        'keyboard': keyboard.get_keyboard(),
        'attachment':''
         }

def get_after_update() -> dict:

    """Создает сообщение после добавления всех данных"""

    return {
        'answer': "Отлично!\nТеперь я могу помочь найти тебе половинку :)",
        'keyboard':find_keyboard.get_keyboard(),
        'attachment':''
        }

def get_hello(name: str) -> dict:

    """Приветствует пользователя"""

    return {
        'answer': f'Привет, {name}!\n' +
        'Я помогу найти тебе половинку :)',
        'keyboard': find_keyboard.get_keyboard(),
        'attachment':''
        }

def get_cities_list(cities: list) -> dict:

    """Если найдено больше одного города"""

    keyboard = VkKeyboard(inline=True)
    count = 1
    for city in cities:
        label = city['title']
        if 'area' in city:
            label += f', {city["area"]}'
        if 'region' in city:
            label += f', {city["region"]}'
        if count % 2 == 0:
            keyboard.add_line()
        keyboard.add_callback_button(
            label=label[:40],
            color=VkKeyboardColor.SECONDARY,
            payload=city['id']
            )
        count += 1
        if count == 10:
            break
    return {
        'answer': 'Выбери нужный город из списка:',
        'keyboard': keyboard.get_keyboard(),
        'attachment':''
        }

def get_recommended_page(data: dict) -> dict:

    """Возвращает рекоммендованную страницу"""

    photos = []
    for photo in data['photos']:
        photos.append(photo['link'])
    attachment = ",".join(photos)
    return {
        'answer': f'vk.com/id{data["id"]}',
        'keyboard': {},
        'attachment': attachment
        }