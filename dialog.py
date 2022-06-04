from FSM import FSM
from aux_functions import check_country, check_city, get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardButton, VkKeyboardColor
from vk_api.bot_longpoll import VkBotEventType
from dialog_msg import DialogMsg as msg

user_token = r'токен пользователя'


class Dialog:

    def __init__(self, vk_bot: object):
        self.bot_brain = FSM(self.begin)
        self.vk_bot = vk_bot
        self.vk_bot_api = vk_bot.get_api()
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        self.cancel_button = keyboard.get_keyboard()

    def send_message(self, msg: str, keyboard=None):
        self.vk_bot_api.messages.send(user_id=self.user_id, message=msg, random_id=get_random_id(), keyboard=keyboard)

    def begin(self, *args):

        if args[0].type == VkBotEventType.MESSAGE_NEW:
            self.user_id = args[0].message['from_id']
        else:
            self.user_id = args[0].obj['user_id']
        user_info = self.vk_bot_api.users.get(user_ids=self.user_id, fields='city, country')[0]
        self.first_name = user_info['first_name']
        if 'city' in user_info:
            self.country = user_info['country']
            self.city = user_info['city']
        else:
            self.country = None
            self.country = None

        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        keyboard.add_callback_button('Старт', color=VkKeyboardColor.POSITIVE, payload={'text': 'start'})
        message = msg.begin(self.first_name)
        self.send_message(message, keyboard.get_keyboard())
        self.bot_brain.set_state(self.cancel_start)

    def cancel_start(self, *args):
        if args[0].type != VkBotEventType.MESSAGE_EVENT:
            return
        if args[0].obj['payload']['text'] == 'start':
            if self.city:
                message = msg.cancel_start(self.country['title'], self.city['title'])
                keyboard = VkKeyboard()
                keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
                keyboard.add_callback_button('Ввести', color=VkKeyboardColor.SECONDARY, payload={'text': 'input'})
                keyboard.add_callback_button('Продолжить', color=VkKeyboardColor.PRIMARY, payload={'text': 'continue'})
                self.send_message(message, keyboard.get_keyboard())
                self.bot_brain.set_state(self.select_city_input_method)
            else:
                message = msg.cancel_start_1()
                self.send_message(message, self.cancel_button)
                self.bot_brain.set_state(self.get_country)

        elif args[0].text == 'cancel':
            pass

    def select_city_input_method(self, *args):
        if args[0].type != VkBotEventType.MESSAGE_EVENT:
            return
        if args[0].obj['payload']['text'] == 'continue':
            message = msg.select_city_input_method()
            self.send_message(message, self.cancel_button)
            self.bot_brain.set_state(self.age_from)
        elif args[0].obj['payload']['text'] == 'input':
            message = msg.select_city_input_method_2()
            self.send_message(message, self.cancel_button)
            self.bot_brain.set_state(self.get_country)
        elif args[0].obj['payload']['text'] == 'cancel':
            pass

    def get_country(self, *args):
        if args[0].type == VkBotEventType.MESSAGE_NEW:
            country = check_country(country=args[0].message['text'], token=user_token)
            if country:
                self.country = country
                message = msg.get_country()
                self.send_message(message, self.cancel_button)
                self.bot_brain.set_state(self.get_city)
            else:
                message = msg.get_country_2()
                self.send_message(message, self.cancel_button)
        else:
            if args[0].obj['payload']['text'] == 'cancel':
                pass

    def get_city(self, *args):
        if args[0].type == VkBotEventType.MESSAGE_NEW:
            cities = check_city(country=self.country['id'], city=args[0].message['text'], token=user_token)
            if not cities:
                self.send_message(msg.get_city())
                return
            if len(cities) > 14:
                self.send_message(msg.get_city_2())
                return
            self.city = cities
            self.send_message(msg.get_city_4(cities))
            self.send_message(msg.get_city_3(), self.cancel_button)
            self.bot_brain.set_state(self.select_city)
        else:
            pass

    def select_city(self, *args):
        if args[0].type == VkBotEventType.MESSAGE_NEW:
            try:
                index = int(args[0].message['text'])
                if index < 1:
                    raise ValueError
                self.city = self.city[index-1]
                self.bot_brain.set_state(self.get_age_from)
                self.send_message(msg.select_city())
                self.send_message(msg.select_city_2(), self.cancel_button)
            except (ValueError, IndexError):
                self.send_message(msg.wrong_input())
        else:
            pass



    def get_age_from(self, *args):
        if args[0].type == VkBotEventType.MESSAGE_NEW:
            try:
                self.age_from = int(args[0].message['text'])
                if self.age_from < 16:
                    raise ValueError
                self.bot_brain.set_state(self.get_age_to)
                self.send_message(msg.get_age_from(), self.cancel_button)
            except ValueError:
                self.send_message(msg.wrong_input())
        else:
            pass
    def get_age_to(self, *args):
        if args[0].type == VkBotEventType.MESSAGE_NEW:
            try:
                self.age_to = int(args[0].message['text'])
                if self.age_to > 90:
                    raise ValueError
                if (self.age_to - self.age_from) < 0 or (self.age_to - self.age_from) > 10:
                    self.bot_brain.set_state(self.get_age_from)
                    self.send_message(msg.get_age_to_2(), self.cancel_button)
                    return
                self.bot_brain.set_state(self.get_sex)
                self.send_message(msg.get_age_to(), self.cancel_button)
            except ValueError:
                self.send_message(msg.wrong_input())
        else:
            pass

    def get_sex(self, *args):
        if args[0].type == VkBotEventType.MESSAGE_NEW:
            try:
                self.sex = int(args[0].message['text'])
                if 0 > self.sex > 2:
                    raise ValueError
                self.bot_brain.set_state(self.search)
                self.send_message(msg.get_sex(), self.cancel_button)
                self.bot_brain.update(args[0])
            except ValueError:
                self.send_message(msg.wrong_input())
        else:
            pass

    def search(self, *args):
        pass
