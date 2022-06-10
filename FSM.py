class FSM:
    """
    Мозг бота. Обеспечивает переключение состояний и вызов методов бота.
    """
    def __init__(self, state: object):
        self.active_state = state
        pass

    def set_state(self, state: object):
        """
        Функция переключения состояний.

        :param state: Функция обрабатывающая событие.
        :return:
        """
        self.active_state = state
        pass

    def update(self, event: object):
        """
        Запуск функции обработки события.

        :param event: longpoll событие полученное от сервера Вконтакте.
        :return:
        """
        self.active_state(event)
