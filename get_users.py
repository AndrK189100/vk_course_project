from vk_api import VkApi, ApiError
import datetime


class GetUsers:

    """
    Поиск пользователй Вконтакте по параметрам

    :param vk_user: Взаимодействие с API Вконтакте от имени пользователя бота.
    :type vk_user: VkApi
    """

    def __init__(self, vk_user: VkApi):
        self.__buffer = []
        self.__vk_user = vk_user
        self.__vk_api = vk_user.get_api()

    def __get_dirty_users(self, search_options: dict):
        """
        Поиск пользователей по заданным параметрам.

        :param search_options: словарь с параметрами поиска. Обязательно наличие ключа has_photo
                со значением 1.
        :return: Словарь {'result': 1}, в случае ошибки или пустого результата словарь вида
                {'result': код_ошибки, 'msg': описание}
        """
        if 'has_photo' not in search_options or search_options['has_photo'] == 0:
            return {'result': -4, 'msg': 'argument has photo not found or 0'}

        try:
            items = self.__vk_user.method('users.search', search_options)['items']
            self.__check_field_dirty_users(items, 'last_seen')

        except ApiError as error_msg:
            return {'result': -1, 'msg': error_msg}

        if not items:
            return {'result': -2, 'msg': 'end of users'}

        date_month_ago_str = str(datetime.date.today() - datetime.timedelta(days=30))
        timestamp_month_ago = int(datetime.datetime.strptime(date_month_ago_str, '%Y-%m-%d').timestamp())

        for item in items:
            if item['can_send_friend_request'] == 1 and item['blacklisted_by_me'] == 0 \
                    and item['can_access_closed'] and item['last_seen']['time'] >= timestamp_month_ago:
                self.__buffer.append({'id': item['id'],
                                      'profile': f'https://vk.com/id{item["id"]}',
                                      'first_name': item['first_name'],
                                      'last_name': item['last_name'],
                                      'photos': []
                                      })

        if not self.__buffer:
            return {'result': -3, 'msg': 'selection empty'}
        return {'result': 1}

    def __get_photos(self):
        """
        Получение фотографий найденных объектов, у пользователя должно быть минимум три фотографии

        :return: Словарь {'result': 1}, в случае ошибки или пустого результата словарь вида
                {'result': код_ошибки, 'msg': описание}
        """
        for user in self.__buffer:
            try:
                photos = self.__vk_api.photos.get(owner_id=user['id'], album_id='profile', extended=1)
            except ApiError as error_msg:
                return {'result': -1, 'msg': error_msg}

            photos['items'].sort(key=lambda x: x['likes']['count'], reverse=True)
            if photos['count'] > 2:
                photos = photos['items'][:3]
            else:
                #photos = photos['items']
                continue
            for photo in photos:
                user['photos'].append(f'photo{photo["owner_id"]}_{photo["id"]}')

        self.__check_count_photos_dirty_users(self.__buffer)

        if not self.__buffer:
            return {'result': -3, 'msg': 'selection empty'}
        return {'result': 1}

    def __check_field_dirty_users(self, items: list, field: str):
        """
        Проверка наличия у объекта поля. Вслучае отсутствие удаление объекта из списка найденных.

        :param items: Список объектов.
        :param field: Название поля.

        :return:
        """
        for item in items:
            if field not in item:
                items.remove(item)
                self.__check_field_dirty_users(items, field)

    def __check_count_photos_dirty_users(self, items: list):
        """
        Проверка наличия у объекта миниум трех фотографии. В случае невыполнения условия
        удаление объекта из списка найденных.
        :param items:
        :return:
        """
        for item in items:
            if len(item['photos']) < 3:
                items.remove(item)
                self.__check_count_photos_dirty_users(items)

    def get_users(self, search_options: dict):
        """
        Поиск пользователей Вконтакте по параметрам с минимум тремя фотографиями в профиле.

        :param search_options: словарь параметров поиска. Ключи словаря - поля API Вконтакте.
               Обязательно наличие ключа has_photos со значением 1
        :rtype: list, dict
        :return: Список пользователей, в случае ошибки или пустого результата словарь
                 вида {'result': код_ошибки, 'msg': описание}

        """
        result = self.__get_dirty_users(search_options)
        if result['result'] != 1:
            return result

        result = self.__get_photos()
        if result['result'] != 1:
            return result
        return self.__buffer

    def clear_buffer(self):
        """
        Удаление результата поиска.

        :rtype: None
        :return: None
        """
        self.__buffer.clear()


