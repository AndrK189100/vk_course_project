from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from cp_vk_api import CpVkApi
from dialog import Dialog
import tokens

token = tokens.app_token
buffer = {}
app_id = '8179323'
group_id = '213571095'
client_secret = tokens.client_secret
service_token = tokens.service_token
db_name = 'vkcp'
db_host = 'localhost'
db_user = tokens.db_user
db_password = tokens.db_password
server_url = 'http://vds.bmnet.org:8000'


def main():
    vk_bot = CpVkApi(token=token,
                     service_token=service_token,
                     app_id=app_id,
                     client_secret=client_secret,
                     server_url=server_url,
                     api_version='5.131')

    longpoll_bot = VkBotLongPoll(vk_bot, group_id)

    for event in longpoll_bot.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
            if event.message['from_id'] not in buffer:
                buffer[event.message['from_id']] = Dialog(vk_bot, db_name, db_user, db_password, db_host)
            buffer[event.message['from_id']].bot_brain.update(event)
        elif event.type == VkBotEventType.MESSAGE_EVENT and 'user_id' in event.obj:

            if event.obj['user_id'] not in buffer:
                buffer[event.obj['user_id']] = Dialog(vk_bot, db_name, db_user, db_password, db_host)
            buffer[event.obj['user_id']].bot_brain.update(event)


if __name__ == '__main__':
    main()
