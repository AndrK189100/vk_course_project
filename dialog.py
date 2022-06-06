from json import dumps
from requests import get
from FSM import FSM
import random
from vk_api.keyboard import VkKeyboard, VkKeyboardButton, VkKeyboardColor
from vk_api.bot_longpoll import VkBotEventType
from vk_api import VkApi
from dialog_msg import DialogMsg as msg
from get_users import GetUsers
from search_options import search_options




class Dialog:

    def __init__(self, vk_bot: object):
        self.user_token = None
        self.vk_user = None
        self.sex = None
        self.age_to = None
        self.city = None
        self.country = None
        self.age_from = None
        self.first_name = None
        self.user_id = None
        self.position = 0
        self.bot_brain = FSM(self.begin)
        self.vk_bot_api = vk_bot.get_api()
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        self.cancel_button = keyboard.get_keyboard()
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Начать', color=VkKeyboardColor.PRIMARY, payload={'text': 'start'})
        self.start_button = keyboard.get_keyboard()
        self.empty_keyboard = VkKeyboard().get_empty_keyboard()
        self.result_buffer = []

        self.auth_url = f'https://oauth.vk.com/authorize?' \
                        f'client_id={vk_bot.app_id}&' \
                        f'display=page&' \
                        f'redirect_uri={vk_bot.server_url}&' \
                        f'scope=&' \
                        f'response_type=code&' \
                        f'v=5.131&' \
                        f'state='

        self.token_url = f'https://oauth.vk.com/access_token?' \
                         f'client_id={vk_bot.app_id}&' \
                         f'client_secret={vk_bot.client_secret}&' \
                         f'redirect_uri={vk_bot.server_url}&' \
                         f'code='

    def send_message(self, msg: str, keyboard=None, attachment=None):
        self.vk_bot_api.messages.send(user_id=self.user_id,
                                      message=msg,
                                      random_id=self.get_random_id(),
                                      keyboard=keyboard,
                                      attachment=attachment)

    def send_answer(self, event_id, peer_id, event_data=None):
        self.vk_bot_api.messages.sendMessageEventAnswer(event_id=event_id,
                                                        user_id=self.user_id,
                                                        peer_id=peer_id,
                                                        event_data=event_data
                                                        )

    def check_country(self, country: str):
        api = self.vk_user.get_api()
        countries = api.database.getCountries(need_all=1, count=240)
        cap_country = country.capitalize()
        for item in countries['items']:
            if item['title'] == cap_country:
                return item
        return False

    def check_city(self, country: int, city: str) -> bool:
        api = self.vk_user.get_api()
        city = api.database.getCities(q=city, country_id=country, need_all=1)
        if city['count'] > 0:
            return city['items']
        else:
            return False

    def get_random_id(self):
        return random.getrandbits(31) * random.choice([-1, 1])

    def cancel(self, msg: msg, keyboard=None):
        if not keyboard:
            keyboard = self.empty_keyboard
        self.send_message(msg, keyboard)
        self.bot_brain.set_state(self.begin)

    def begin(self, event):

        if event.type == VkBotEventType.MESSAGE_NEW:
            self.user_id = str(event.message['from_id'])
        else:
            self.user_id = str(event.obj['user_id'])
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])

        user_info = self.vk_bot_api.users.get(user_ids=self.user_id, fields='city, country')[0]
        self.first_name = user_info['first_name']

        if 'city' in user_info:
            self.country = user_info['country']
            self.city = user_info['city']

        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        keyboard.add_callback_button('Авторизация', color=VkKeyboardColor.POSITIVE, payload={'text': 'authorize'})
        self.send_message(msg.begin(self.first_name), keyboard.get_keyboard())
        self.bot_brain.set_state(self.pre_authorize)

    def pre_authorize(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return
        if event.obj['payload']['text'] == 'authorize':
            self.send_answer(event.obj['event_id'],
                             event.obj['peer_id'],
                             event_data=dumps({'type': 'open_link', 'link': self.auth_url + self.user_id}))
            keyboard = VkKeyboard()
            keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
            keyboard.add_callback_button('Продолжить', color=VkKeyboardColor.POSITIVE, payload={'text': 'proceed'})
            self.send_message(msg.pre_authorize(), keyboard.get_keyboard())
            self.bot_brain.set_state(self.authorize)

        elif event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.start_button)

            pass

    def authorize(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return
        self.send_answer(event.obj['event_id'], event.obj['peer_id'])
        if event.obj['payload']['text'] == 'proceed':
            resp = get(f'http://localhost:8000/user_code?user_id={self.user_id}').json()
            if not resp:
                self.cancel(msg.authorize_wrong(), self.start_button)
                return
            resp = get(self.token_url + resp)
            if resp.status_code != 200:
                self.cancel(msg.authorize_wrong(), self.start_button)
                return
            user_token = resp.json()['access_token']
            self.vk_user = VkApi(token=user_token)
            self.user_token = user_token
            self.found_users = GetUsers(self.vk_user)
            self.send_message(msg.authorize())
            self.bot_brain.set_state(self.start)
            self.bot_brain.update(event)
        elif event.obj['payload']['text'] == 'cancel':
            self.cancel(msg.cancel(), self.start_button)

    def start(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return
        if event.obj['payload']['text'] == 'proceed':
            if self.city:
                message = msg.cancel_start(self.country['title'], self.city['title'])
                keyboard = VkKeyboard()
                keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
                keyboard.add_callback_button('Ввести', color=VkKeyboardColor.SECONDARY, payload={'text': 'input'})
                keyboard.add_callback_button('Продолжить', color=VkKeyboardColor.PRIMARY, payload={'text': 'proceed'})
                self.send_message(message, keyboard.get_keyboard())
                self.bot_brain.set_state(self.select_city_input_method)
            else:
                keyboard = VkKeyboard()
                keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
                keyboard.add_callback_button('Продолжить', color=VkKeyboardColor.PRIMARY, payload={'text': 'proceed'})
                self.send_message(msg.cancel_start_1(), keyboard.get_keyboard())
                self.bot_brain.set_state(self.get_country)

        elif event.obj['payload']['text'] == 'cancel':
            self.cancel(msg.cancel(), self.start_button)

    def select_city_input_method(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return
        self.send_answer(event.obj['event_id'], event.obj['peer_id'])
        if event.obj['payload']['text'] == 'proceed':
            self.send_message(msg.select_city_input_method(), self.cancel_button)
            self.bot_brain.set_state(self.get_age_from)
        elif event.obj['payload']['text'] == 'input':
            self.send_message(msg.select_city_input_method_2(), self.cancel_button)
            self.bot_brain.set_state(self.get_country)
        elif event.obj['payload']['text'] == 'cancel':
            self.cancel(msg.cancel())

    def get_country(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            country = self.check_country(country=event.message['text'])
            if country:
                self.country = country
                message = msg.get_country()
                self.send_message(message, self.cancel_button)
                self.bot_brain.set_state(self.get_city)
            else:
                message = msg.get_country_2()
                self.send_message(message, self.cancel_button)
        elif event.type == VkBotEventType.MESSAGE_EVENT and event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.start_button)

    def get_city(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            cities = self.check_city(country=self.country['id'], city=event.message['text'])
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
        elif event.type == VkBotEventType.MESSAGE_EVENT and event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.start_button)

    def select_city(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                index = int(event.message['text'])
                if index < 1:
                    raise ValueError
                self.city = self.city[index - 1]
                self.bot_brain.set_state(self.get_age_from)
                self.send_message(msg.select_city())
                self.send_message(msg.select_city_2(), self.cancel_button)
            except (ValueError, IndexError):
                self.send_message(msg.wrong_input())
        elif event.type == VkBotEventType.MESSAGE_EVENT and event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.start_button)

    def get_age_from(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                self.age_from = int(event.message['text'])
                if self.age_from < 16:
                    raise ValueError
                self.bot_brain.set_state(self.get_age_to)
                self.send_message(msg.get_age_from(), self.cancel_button)
            except ValueError:
                self.send_message(msg.wrong_input())
        elif event.type == VkBotEventType.MESSAGE_EVENT and event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.start_button)

    def get_age_to(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                self.age_to = int(event.message['text'])
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
        elif event.type == VkBotEventType.MESSAGE_EVENT and event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.start_button)

    def get_sex(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                self.sex = int(event.message['text'])
                if self.sex < 0 or self.sex > 2:
                    raise ValueError
                self.bot_brain.set_state(self.search)
                keyboard = VkKeyboard()
                keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
                keyboard.add_callback_button('Продолжить', color=VkKeyboardColor.PRIMARY, payload={'text': 'proceed'})
                self.send_message(msg.get_sex(self.city['title'],
                                              self.sex,
                                              self.age_from,
                                              self.age_to),
                                  keyboard.get_keyboard())
                search_options['offset'] = 0
                search_options['city'] = self.city['id']
                search_options['sex'] = self.sex
                search_options['age_from'] = self.age_from
                search_options['age_to'] = self.age_to

            except ValueError:
                self.send_message(msg.wrong_input())
        elif event.type == VkBotEventType.MESSAGE_EVENT and event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.start_button)

    def search(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return
        self.send_answer(event.obj['event_id'], event.obj['peer_id'])
        if event.obj['payload']['text'] == 'proceed':
            keyboard = VkKeyboard()
            keyboard.add_callback_button('<<', VkKeyboardColor.PRIMARY, {'text': '<<'})
            keyboard.add_callback_button('*', VkKeyboardColor.PRIMARY, {'text': '*'})
            keyboard.add_callback_button('>>', VkKeyboardColor.PRIMARY, {'text': '>>'})
            keyboard.add_line()
            keyboard.add_callback_button('Отмена', VkKeyboardColor.NEGATIVE, {'text': 'cancel'})

            self.send_message(msg.one_moment())

            self.result_buffer += self.found_users.get_users(search_options)
            self.found_users.clear_buffer()
            self.bot_brain.set_state(self.viewer)
            self.bot_brain.update(event)
            self.send_message(msg.list_unstruction(), keyboard.get_keyboard())
            self.send_message(msg.searh_output(self.result_buffer[self.position]['first_name'],
                                               self.result_buffer[self.position]['last_name'],
                                               self.result_buffer[self.position]['profile']),
                              attachment=','.join(self.result_buffer[self.position]['photos']))
        elif event.obj['payload']['text'] == 'cancel':
            self.cancel(msg.cancel(), self.start_button)

    def viewer(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return
        if event.obj['payload']['text'] == '>>':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.position += 1
            if self.position == len(self.result_buffer):
                search_options['offset'] += 10
                self.result_buffer += self.found_users.get_users(search_options)
                self.found_users.clear_buffer()

            self.send_message(msg.searh_output(self.result_buffer[self.position]['first_name'],
                                               self.result_buffer[self.position]['last_name'],
                                               self.result_buffer[self.position]['profile']),
                              attachment=','.join(self.result_buffer[self.position]['photos']))

        elif event.obj['payload']['text'] == '<<':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            if self.position == 0:
                self.send_message(msg.end_of_list())
                return
            self.position -= 1
            self.send_message(msg.searh_output(self.result_buffer[self.position]['first_name'],
                                               self.result_buffer[self.position]['last_name'],
                                               self.result_buffer[self.position]['profile']),
                              attachment=','.join(self.result_buffer[self.position]['photos']))

            pass
        elif event.obj['payload']['text'] == '*':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.send_message(msg.dummy())
            return

        elif event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.start_button)
