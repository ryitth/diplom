"""Модуль обработчика сообщений"""

from random import randrange
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
import business_logic

class MessageHandler:
    """Класс для отслеживания сообщений"""

    def __init__(self, vk_session, group_id) -> None:
        self.vk_session = vk_session
        self.longpoll = VkBotLongPoll(vk=vk_session, group_id=group_id)
        self.api = self.vk_session.get_api()


    def run(self) -> None:

        """Отслеживает поступающие сообщения"""

        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_EVENT:
                self._generate_answer(event.obj.peer_id, f'dante{event.obj.payload}termo')
                
            if event.type == VkBotEventType.MESSAGE_NEW:
                self._generate_answer(event.message.from_id, event.message.text)


    def _send_message(self, user_id: int, answer: str, attachment:str, keyboard: dict) -> None:
        self.api.messages.send(
            keyboard=keyboard,
            user_id=user_id,
            message=answer,
            random_id=randrange(10 ** 7),
            attachment=attachment
            )

    def _generate_answer(self, user_id: int, message: str) -> None:
        data_answer = business_logic.action(user_id, message)
        if data_answer:
            self._send_message(
                user_id=user_id,
                answer=data_answer['answer'],
                keyboard=data_answer['keyboard'],
                attachment=data_answer['attachment']
                )
