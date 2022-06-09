from json import dumps
from requests import get
from FSM import FSM
import random
from vk_api.bot_longpoll import VkBotEventType
from vk_api import VkApi, ApiError
from dialog_msg import DialogMsg as msg
from get_users import GetUsers
from search_options import search_options
from bot_keyboard import BotKeyboard
from cp_db import CpDb
import tokens


class Dialog:

    def __init__(self, vk_bot: object, db_name: str, db_user: str, db_password: str, db_host: str):
        self.found_users = None
        self.user_token = None
        self.vk_user = None
        self.sex = None
        self.age_to = None
        self.city = None
        self.cities = None
        self.country = None
        self.age_from = None
        self.first_name = None
        self.user_id = None
        self.position = 0
        self.bot_keyboard = BotKeyboard()
        self.bot_brain = FSM(self.begin)
        self.vk_bot_api = vk_bot.get_api()
        self.vk_service_api = VkApi(token=vk_bot.service_token).get_api()
        self.db_interaction = CpDb(db_name, db_user, db_password, db_host)
        self.search_options = search_options.copy()
        self.server_url = vk_bot.server_url

        self.auth_url = f'https://oauth.vk.com/authorize?' \
                        f'client_id={vk_bot.app_id}&' \
                        f'display=page&' \
                        f'redirect_uri={vk_bot.server_url}/send_code&' \
                        f'scope=&' \
                        f'response_type=code&' \
                        f'v=5.131&' \
                        f'state='

        self.token_url = f'https://oauth.vk.com/access_token?' \
                         f'client_id={vk_bot.app_id}&' \
                         f'client_secret={vk_bot.client_secret}&' \
                         f'redirect_uri={vk_bot.server_url}/send_code&' \
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

    def check_token(self, user_token: str):
        result = self.vk_service_api.secure.checkToken(token=user_token)
        if result['success'] == 1:
            return True
        else:
            return False

    def get_random_id(self):
        return random.getrandbits(31) * random.choice([-1, 1])

    def cancel(self, msg: msg, keyboard=None):
        if not keyboard:
            keyboard = self.bot_keyboard.empty_keyboard()
        self.send_message(msg, keyboard)
        self.bot_brain.set_state(self.begin)
        self.db_interaction.clear_found_user(self.user_id)
        self.position = 0

    def get_favorites(self):
        favorite_users = self.db_interaction.get_favorites(self.user_id)
        if favorite_users:
            self.send_message(msg.favorite())
            for user in favorite_users:
                self.send_message(msg.searh_output(user[2].strip(),
                                                   user[3].strip(),
                                                   user[4].strip()),
                                  attachment=user[5])
            self.send_message(msg.favorite_end())
        else:
            self.send_message(msg.empty())

    def begin(self, event):

        if event.type == VkBotEventType.MESSAGE_NEW:
            self.user_id = str(event.message['from_id'])
        else:
            self.user_id = str(event.obj['user_id'])
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])

        self.db_interaction.clear_found_user(self.user_id)

        user_bot_data = self.db_interaction.get_bot_user(self.user_id)
        if user_bot_data:
            if user_bot_data[0][1]:
                self.user_token = user_bot_data[0][1].strip()
        else:
            self.db_interaction.insert_bot_user(self.user_id)

        if self.user_token:
            try:
                if not self.check_token(self.user_token):
                    raise ApiError
                self.bot_brain.set_state(self.start)
                self.vk_user = VkApi(token=self.user_token)
                self.found_users = GetUsers(self.vk_user)
                self.first_name = user_bot_data[0][2]
                self.city = user_bot_data[0][4]
                self.country = user_bot_data[0][3]
                self.send_message(msg.authorized_begin(self.first_name),
                                  self.bot_keyboard.cancel_favorite_begin_keyboard())
                return
            except ApiError:
                self.user_token = None
                self.vk_user = None
                self.sex = None
                self.age_to = None
                self.city = None
                self.cities = None
                self.country = None
                self.age_from = None
                self.first_name = None
                self.position = 0
                self.result_buffer = []
                self.search_options['offset'] = 0

        user_info = self.vk_bot_api.users.get(user_ids=self.user_id, fields='city, country')[0]
        self.first_name = user_info['first_name']

        if 'city' in user_info:
            self.country = user_info['country']
            self.city = user_info['city']
            self.db_interaction.update_bot_user_info(self.user_id,
                                                     user_info['first_name'],
                                                     dumps(user_info['city']),
                                                     dumps(user_info['country']))
        else:
            self.db_interaction.update_bot_user_info(self.user_id, user_info['first_name'])

        self.send_message(msg.begin(self.first_name), self.bot_keyboard.authorize_keyboard())
        self.bot_brain.set_state(self.pre_authorize)

    def pre_authorize(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return
        if event.obj['payload']['text'] == 'authorize':
            self.send_answer(event.obj['event_id'],
                             event.obj['peer_id'],
                             event_data=dumps({'type': 'open_link', 'link': self.auth_url + self.user_id}))

            self.send_message(msg.pre_authorize(), self.bot_keyboard.cancel_proceed_keyboard())
            self.bot_brain.set_state(self.authorize)

        elif event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())

            pass

    def authorize(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return
        self.send_answer(event.obj['event_id'], event.obj['peer_id'])
        if event.obj['payload']['text'] == 'proceed':
            resp = get(f'{self.server_url}/user_code?user_id={self.user_id}').json()
            if not resp:
                self.cancel(msg.authorize_wrong(), self.bot_keyboard.start_keyboard())
                return
            resp = get(self.token_url + resp)
            if resp.status_code != 200:
                self.cancel(msg.authorize_wrong(), self.bot_keyboard.start_keyboard())
                return
            self.user_token = resp.json()['access_token']
            self.vk_user = VkApi(token=self.user_token)
            self.db_interaction.update_bot_user_token(self.user_id, self.user_token)
            self.found_users = GetUsers(self.vk_user)
            self.send_message(msg.authorize())
            self.bot_brain.set_state(self.start)
            self.bot_brain.update(event)
        elif event.obj['payload']['text'] == 'cancel':
            self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())

    def start(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return

        if event.obj['payload']['text'] == 'proceed' or \
                event.obj['payload']['text'] == 'change' or \
                event.obj['payload']['text'] == 'begin' or \
                event.obj['payload']['text'] == 'favorite':

            if event.obj['payload']['text'] == 'favorite':
                self.send_answer(event.obj['event_id'], event.obj['peer_id'])
                self.get_favorites()
                return

            if event.obj['payload']['text'] == 'change' or event.obj['payload']['text'] == 'begin':
                self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            if self.city:
                message = msg.cancel_start(self.country['title'], self.city['title'])

                self.send_message(message, self.bot_keyboard.cancel_input_proceed_keyboard())
                self.bot_brain.set_state(self.select_city_input_method)
            else:
                self.cancel(msg.not_city(), self.bot_keyboard.cancel_favorite_keyboard())
                self.bot_brain.set_state(self.get_country)

        elif event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())

    def select_city_input_method(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return
        self.send_answer(event.obj['event_id'], event.obj['peer_id'])

        if event.obj['payload']['text'] == 'proceed':
            self.send_message(msg.select_city_input_method(), self.bot_keyboard.cancel_favorite_keyboard())
            self.bot_brain.set_state(self.get_age_from)
        elif event.obj['payload']['text'] == 'input':
            self.send_message(msg.select_city_input_method_2(), self.bot_keyboard.cancel_favorite_keyboard())
            self.bot_brain.set_state(self.get_country)
        elif event.obj['payload']['text'] == 'cancel':
            self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())
        elif event.obj['payload']['text'] == 'favorite':
            self.get_favorites()

    def get_country(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            country = self.check_country(country=event.message['text'])
            if country:
                self.country = country
                message = msg.get_country()
                self.send_message(message, self.bot_keyboard.cancel_favorite_keyboard())
                self.bot_brain.set_state(self.get_city)
            else:
                message = msg.get_country_2()
                self.send_message(message, self.bot_keyboard.cancel_favorite_keyboard())
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            if event.obj['payload']['text'] == 'cancel':
                self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())
            elif event.obj['payload']['text'] == 'favorite':
                self.get_favorites()

    def get_city(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            cities = self.check_city(country=self.country['id'], city=event.message['text'])
            if not cities:
                self.send_message(msg.get_city())
                return
            if len(cities) > 20:
                self.send_message(msg.get_city_2())
                return
            self.cities = cities
            self.send_message(msg.get_city_4(cities))
            self.send_message(msg.get_city_3(), self.bot_keyboard.cancel_favorite_keyboard())
            self.bot_brain.set_state(self.select_city)
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            if event.obj['payload']['text'] == 'cancel':
                self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())
            elif event.obj['payload']['text'] == 'favorite':
                self.get_favorites()

    def select_city(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                index = int(event.message['text'])
                if index < 1:
                    raise ValueError
                self.city = self.cities[index - 1]
                self.db_interaction.update_bot_user_info(self.user_id,
                                                         self.first_name,
                                                         dumps(self.city),
                                                         dumps(self.country)
                                                         )
                self.bot_brain.set_state(self.get_age_from)
                self.send_message(msg.select_city())
                self.send_message(msg.select_city_2(), self.bot_keyboard.cancel_favorite_keyboard())
            except (ValueError, IndexError):
                self.send_message(msg.wrong_input())
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            if event.obj['payload']['text'] == 'cancel':
                self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())
            elif event.obj['payload']['text'] == 'favorite':
                self.get_favorites()

    def get_age_from(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                self.age_from = int(event.message['text'])
                if self.age_from < 16:
                    raise ValueError
                self.bot_brain.set_state(self.get_age_to)
                self.send_message(msg.get_age_from(), self.bot_keyboard.cancel_favorite_keyboard())
            except ValueError:
                self.send_message(msg.wrong_input())
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            if event.obj['payload']['text'] == 'cancel':
                self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())
            elif event.obj['payload']['text'] == 'favorite':
                self.get_favorites()

    def get_age_to(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                self.age_to = int(event.message['text'])
                if self.age_to > 90:
                    raise ValueError
                if (self.age_to - self.age_from) < 0 or (self.age_to - self.age_from) > 10:
                    self.bot_brain.set_state(self.get_age_from)
                    self.send_message(msg.get_age_to_2(), self.bot_keyboard.cancel_favorite_keyboard())
                    return
                self.bot_brain.set_state(self.get_sex)
                self.send_message(msg.get_age_to(), self.bot_keyboard.cancel_favorite_keyboard())
            except ValueError:
                self.send_message(msg.wrong_input())
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            if event.obj['payload']['text'] == 'cancel':
                self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())
            elif event.obj['payload']['text'] == 'favorite':
                self.get_favorites()

    def get_sex(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                self.sex = int(event.message['text'])
                if self.sex < 0 or self.sex > 2:
                    raise ValueError
                self.bot_brain.set_state(self.search)
                self.send_message(msg.get_sex(self.city['title'],
                                              self.sex,
                                              self.age_from,
                                              self.age_to),
                                  self.bot_keyboard.cancel_proceed_favorite_keyboard())
                self.search_options['offset'] = 0
                self.search_options['city'] = self.city['id']
                self.search_options['sex'] = self.sex
                self.search_options['age_from'] = self.age_from
                self.search_options['age_to'] = self.age_to

            except ValueError:
                self.send_message(msg.wrong_input())
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            if event.obj['payload']['text'] == 'cancel':
                self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())
            elif event.obj['payload']['text'] == 'favorite':
                self.get_favorites()

    def search(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return
        self.send_answer(event.obj['event_id'], event.obj['peer_id'])
        if event.obj['payload']['text'] == 'proceed':

            self.send_message(msg.one_moment())
            result = self.found_users.get_users(self.search_options)

            if not isinstance(result, list):
                if result['result'] == -1:
                    self.cancel(msg.bot_broken(), self.bot_keyboard.start_keyboard())
                    return
                elif result['result'] == -2 or result['result'] == -3:
                    self.send_message(msg.not_found_users(), self.bot_keyboard.cancel_change_keyboard())
                    self.bot_brain.set_state(self.start)
                    return

            for item in result:
                self.db_interaction.insert_found_user(item['id'], self.user_id, item['first_name'], item['last_name'],
                                                      item['profile'], ','.join(item['photos']))

            self.found_users.clear_buffer()
            self.bot_brain.set_state(self.viewer)
            user = self.db_interaction.get_found_user(user_id=self.user_id, offset=self.position)
            self.send_message(msg.list_unstruction(), self.bot_keyboard.viewer_keyboard())
            self.send_message(msg.searh_output(user[0][0].strip(),
                                               user[0][1].strip(),
                                               user[0][2].strip()),
                              attachment=user[0][3])
            self.bot_brain.update(event)
        elif event.obj['payload']['text'] == 'cancel':
            self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())

        elif event.obj['payload']['text'] == 'favorite':
            self.get_favorites()

    def viewer(self, event):
        if event.type != VkBotEventType.MESSAGE_EVENT:
            return

        if event.obj['payload']['text'] == '>>':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.position += 1
            user = self.db_interaction.get_found_user(user_id=self.user_id, offset=self.position)
            if not user:
                self.search_options['offset'] += 10
                result = self.found_users.get_users(self.search_options)
                if not isinstance(result, list):
                    if result['result'] == -1:
                        self.cancel(msg.bot_broken(), self.bot_keyboard.start_keyboard())
                        return
                    elif result['result'] == -2 or result['result'] == -3:
                        self.send_message(msg.end_of_list())
                        self.position -= 1
                        return
                for item in result:
                    self.db_interaction.insert_found_user(item['id'], self.user_id, item['first_name'],
                                                          item['last_name'],
                                                          item['profile'], ','.join(item['photos']))
                self.found_users.clear_buffer()
                user = self.db_interaction.get_found_user(user_id=self.user_id, offset=self.position)

            self.send_message(msg.searh_output(user[0][0].strip(),
                                               user[0][1].strip(),
                                               user[0][2].strip()),
                              attachment=user[0][3])

        elif event.obj['payload']['text'] == '<<':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            if self.position == 0:
                self.send_message(msg.begin_of_list())
                return
            self.position -= 1
            user = self.db_interaction.get_found_user(user_id=self.user_id, offset=self.position)
            self.send_message(msg.searh_output(user[0][0].strip(),
                                               user[0][1].strip(),
                                               user[0][2].strip()),
                              attachment=user[0][3])

        elif event.obj['payload']['text'] == '*':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            user = self.db_interaction.get_found_user(user_id=self.user_id, offset=self.position)
            self.db_interaction.insert_to_favorites(user[0][4],
                                                    user[0][5],
                                                    user[0][0],
                                                    user[0][1],
                                                    user[0][2],
                                                    user[0][3])
            self.send_message(msg.added())
            return
        elif event.obj['payload']['text'] == 'favorite':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.get_favorites()

        elif event.obj['payload']['text'] == 'cancel':
            self.send_answer(event.obj['event_id'], event.obj['peer_id'])
            self.cancel(msg.cancel(), self.bot_keyboard.start_keyboard())
