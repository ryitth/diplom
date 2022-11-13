"""Модуль бота"""

import vk_api
from message_handler import MessageHandler
from bot_config import API_TOKEN, GROUP_ID

def main():
    """main"""
    vk_session = vk_api.VkApi(token=API_TOKEN)
    
    message_handler = MessageHandler(vk_session, GROUP_ID)
    message_handler.run()


if __name__ == "__main__":
    main()
