import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from dialog import Dialog

token = r'токен приложения'

buffer = {}


if __name__ == '__main__':

    vk_bot = vk_api.VkApi(token=token)
    vk_bot_api = vk_bot.get_api()

    longpoll_bot = VkBotLongPoll(vk_bot, '213571095')

    for event in longpoll_bot.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.message['from_id'] not in buffer:
                buffer[event.message['from_id']] = Dialog(vk_bot)
            buffer[event.message['from_id']].bot_brain.update(event)
        elif event.type == VkBotEventType.MESSAGE_EVENT and 'user_id' in event.obj:
            vk_bot_api.messages.sendMessageEventAnswer(event_id=event.obj.event_id,
                                                       user_id=event.obj.user_id,
                                                       peer_id=event.obj.peer_id
                                                       )
            if event.obj['user_id'] not in buffer:
                buffer[event.obj['user_id']] = Dialog(vk_bot)
            buffer[event.obj['user_id']].bot_brain.update(event)
