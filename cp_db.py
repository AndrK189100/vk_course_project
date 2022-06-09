import psycopg2


class CpDb:

    def __init__(self, db_name: str, db_user: str, db_password: str, db_host: str):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.conn = None

    def get_cursor(self):
        self.conn = psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_password, host=self.db_host)
        return self.conn.cursor()

    def del_cursor(self, cursor):
        cursor.close()
        self.conn.close()

    def get_bot_user(self, user_id: int):
        query = 'SELECT * FROM botusers WHERE user_id = %s'

        cursor = self.get_cursor()
        cursor.execute(query, [user_id])
        record = cursor.fetchall()
        self.del_cursor(cursor)
        return record

    def insert_bot_user(self, user_id: int, user_token=None):
        query = 'INSERT INTO botusers VALUES(%s, %s)'
        cursor = self.get_cursor()
        cursor.execute(query, [user_id, user_token])
        self.conn.commit()
        self.del_cursor(cursor)

    def update_bot_user_token(self, user_id: int, user_token: str):
        query = 'UPDATE botusers SET user_token = %s WHERE user_id = %s'
        cursor = self.get_cursor()
        cursor.execute(query, [user_token, user_id])
        self.conn.commit()
        self.del_cursor(cursor)

    def update_bot_user_info(self, user_id: int, first_name: str, user_city=None, user_country=None):
        query = 'UPDATE botusers SET firstname = %s, user_country = %s, user_city = %s WHERE user_id = %s'
        cursor = self.get_cursor()
        cursor.execute(query, [first_name, user_country, user_city, user_id])
        self.conn.commit()
        self.del_cursor(cursor)

    def del_bot_user(self, user_id: int):
        query = 'DELETE FROM botusers WHERE user_id = %s'
        cursor = self.get_cursor()
        cursor.execute(query, [user_id])
        self.conn.commit()
        self.del_cursor(cursor)

    def get_found_user(self, user_id: int, offset: int):
        query = 'SELECT firstname, lastname, profile, photos, user_id, found_id FROM foundusers ' \
                'WHERE user_id = %s ORDER BY num LIMIT 1 OFFSET %s'
        cursor = self.get_cursor()
        cursor.execute(query, [user_id, offset])
        record = cursor.fetchall()
        self.del_cursor(cursor)
        return record

    def insert_found_user(self, found_id: int,
                          user_id: int,
                          first_name: str,
                          last_name: str,
                          profile: str,
                          photos: str):
        query = 'INSERT INTO foundusers VALUES(%s, %s, %s, %s, %s, %s) ' \
                'ON CONFLICT (found_id) DO NOTHING;'
        cursor = self.get_cursor()
        cursor.execute(query, [found_id, user_id, first_name, last_name, profile, photos])
        self.conn.commit()
        self.del_cursor(cursor)

    def clear_found_user(self, user_id: int):
        query = 'DELETE FROM foundusers WHERE user_id = %s'
        cursor = self.get_cursor()
        cursor.execute(query, [user_id])
        self.conn.commit()
        self.del_cursor(cursor)

    def insert_to_favorites(self, user_id: int,
                            found_id: int,
                            first_name: str,
                            last_name: str,
                            profile: str,
                            photos: str):
        query = 'INSERT INTO favorites VALUES(%s, %s, %s, %s, %s, %s) ' \
                'ON CONFLICT (user_id, found_id) DO NOTHING;'
        cursor = self.get_cursor()
        cursor.execute(query, [user_id, found_id, first_name, last_name, profile, photos])
        self.conn.commit()
        self.del_cursor(cursor)

    def get_favorites(self, user_id: int):
        query = 'SELECT * FROM favorites WHERE user_id=%s'
        cursor = self.get_cursor()
        cursor.execute(query, [user_id])
        record = cursor.fetchall()
        self.del_cursor(cursor)
        return record

