import psycopg2


class CpDb:
    """
    Класс взаимодействия с базой данных.

    :param db_name: Имя базы данных
    :type db_name: str
    :param db_user: Пользователь базы данных
    :type db_user: str
    :param db_password: Пароль пользователя базы данных
    :type db_password: str
    :param db_host: Адрес сервера базы данных
    :type db_host: str
    """

    def __init__(self, db_name: str, db_user: str, db_password: str, db_host: str):

        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.conn = None

    def __get_cursor(self):
        self.conn = psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_password, host=self.db_host)
        return self.conn.cursor()

    def __del_cursor(self, cursor):
        cursor.close()
        self.conn.close()

    def get_bot_user(self, user_id: int):
        """
        Получение пользователя бота из базы данных.

        :param user_id: идентификатор пользователя
        :type user_id: int
        :return: Список с одним элементом типа touple содежращий все поля таблицы.
        :rtype: list
        """
        query = 'SELECT * FROM botusers WHERE user_id = %s'

        cursor = self.__get_cursor()
        cursor.execute(query, [user_id])
        record = cursor.fetchall()
        self.__del_cursor(cursor)
        return record

    def insert_bot_user(self, user_id: int, user_token=None):
        """
        Добавление пользователя бота в базу данных.

        :param user_id: идентификатор пользователя
        :type user_id: int
        :param user_token: токен пользователя Вконтакте
        :type user_token: str
        :rtype: None
        """
        query = 'INSERT INTO botusers VALUES(%s, %s)'
        cursor = self.__get_cursor()
        cursor.execute(query, [user_id, user_token])
        self.conn.commit()
        self.__del_cursor(cursor)

    def update_bot_user_token(self, user_id: int, user_token: str):
        """
        Обновление токена пользователя бота.

        :param user_id: идентификатор пользователя
        :type user_id: int
        :param user_token: токен пользователя Вконтакте
        :type user_token: str
        :rtype: None
        """
        query = 'UPDATE botusers SET user_token = %s WHERE user_id = %s'
        cursor = self.__get_cursor()
        cursor.execute(query, [user_token, user_id])
        self.conn.commit()
        self.__del_cursor(cursor)

    def update_bot_user_info(self, user_id: int, first_name: str, user_city=None, user_country=None):
        """
        Обновление личной информации пользователя бота.

        :param user_id: идентификатор пользователя
        :type user_id: int
        :param first_name: Имя
        :type first_name: str
        :param user_city: Город, defaults to None
        :type user_city: object
        :param user_country: Страна, defaults to None
        :type user_country: object
        :return:
        """
        query = 'UPDATE botusers SET firstname = %s, user_country = %s, user_city = %s WHERE user_id = %s'
        cursor = self.__get_cursor()
        cursor.execute(query, [first_name, user_country, user_city, user_id])
        self.conn.commit()
        self.__del_cursor(cursor)

    def del_bot_user(self, user_id: int):
        """
        Удаление пользователя бота из базы данных

        :param user_id: идентификатор пользователя
        :type: user_id: int
        :return:
        """
        query = 'DELETE FROM botusers WHERE user_id = %s'
        cursor = self.__get_cursor()
        cursor.execute(query, [user_id])
        self.conn.commit()
        self.__del_cursor(cursor)

    def get_found_user(self, user_id: int, offset: int):
        """
        Получение найденного пользователя из базы данных.

        :param user_id: Идентификатор пользователя
        :param offset: Смещение относительно первого найденого результата.
        :return: Список с одним элементом типа touple содержащий поля:
                 firstname, lastname, profile, photos, user_id, found_id
        :rtype list
        """
        query = 'SELECT firstname, lastname, profile, photos, user_id, found_id FROM foundusers ' \
                'WHERE user_id = %s ORDER BY num LIMIT 1 OFFSET %s'
        cursor = self.__get_cursor()
        cursor.execute(query, [user_id, offset])
        record = cursor.fetchall()
        self.__del_cursor(cursor)
        return record

    def insert_found_user(self, found_id: int,
                          user_id: int,
                          first_name: str,
                          last_name: str,
                          profile: str,
                          photos: str):
        """
        Добавление найденного пользователя в базу данных.

        :param found_id: идентификатор найденного пользователя.
        :param user_id: идентификатор пользователя бота.
        :param first_name: Имя найденного пользователя.
        :param last_name: Фамилия найденного пользователя.
        :param profile: Ссылка на профиль найденного пользователя.
        :param photos: Строка содержащая фотографии найденного пользователя.
        :return:
        """
        query = 'INSERT INTO foundusers VALUES(%s, %s, %s, %s, %s, %s) ' \
                'ON CONFLICT (found_id) DO NOTHING;'
        cursor = self.__get_cursor()
        cursor.execute(query, [found_id, user_id, first_name, last_name, profile, photos])
        self.conn.commit()
        self.__del_cursor(cursor)

    def clear_found_user(self, user_id: int):
        """
        Удаление всех найденных пользователей пользователя бота.

        :param user_id: Идентификатор пользователя бота.
        :return:
        """
        query = 'DELETE FROM foundusers WHERE user_id = %s'
        cursor = self.__get_cursor()
        cursor.execute(query, [user_id])
        self.conn.commit()
        self.__del_cursor(cursor)

    def insert_to_favorites(self, user_id: int,
                            found_id: int,
                            first_name: str,
                            last_name: str,
                            profile: str,
                            photos: str):
        """
        Добавление найденного пользователя в избранное.

        :param user_id: Идентификатор пользователя бота.
        :param found_id: Идентификатор найденного пользователя.
        :param first_name: Имя найденного пользователя.
        :param last_name: Фамилия найденного пользователя.
        :param profile: Ссылка на профиль найденного пользователя.
        :param photos: Строка содержащая фотографии найденого пользователя.
        :return:
        """
        query = 'INSERT INTO favorites VALUES(%s, %s, %s, %s, %s, %s) ' \
                'ON CONFLICT (user_id, found_id) DO NOTHING;'
        cursor = self.__get_cursor()
        cursor.execute(query, [user_id, found_id, first_name, last_name, profile, photos])
        self.conn.commit()
        self.__del_cursor(cursor)

    def get_favorites(self, user_id: int):
        """
        Получения пользователя из избранного.

        :param user_id: Идентификатор пользователя бота
        :return: Список с одним элементом типа toupe содержащий поля:
                 user_id, found_id, first_name, last_name, profile, photos.
        :rtype: list
        """
        query = 'SELECT * FROM favorites WHERE user_id=%s'
        cursor = self.__get_cursor()
        cursor.execute(query, [user_id])
        record = cursor.fetchall()
        self.__del_cursor(cursor)
        return record

