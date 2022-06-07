from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from cp_vk_api import CpVkApi
from dialog import Dialog

token = r'токен приложения'

buffer = {}
app_id = '8179323'
group_id = '213571095'
client_secret = 'секретный ключ приложения'

server_url = 'http://localhost:8000'

if __name__ == '__main__':

    vk_bot = CpVkApi(token=token, app_id=app_id, client_secret=client_secret, server_url=server_url)

    longpoll_bot = VkBotLongPoll(vk_bot, group_id)

    for event in longpoll_bot.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
            if event.message['from_id'] not in buffer:
                buffer[event.message['from_id']] = Dialog(vk_bot)
            buffer[event.message['from_id']].bot_brain.update(event)
        elif event.type == VkBotEventType.MESSAGE_EVENT and 'user_id' in event.obj:

            if event.obj['user_id'] not in buffer:
                buffer[event.obj['user_id']] = Dialog(vk_bot)
            buffer[event.obj['user_id']].bot_brain.update(event)



