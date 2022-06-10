import vk_api


class CpVkApi(vk_api.VkApi):
    """
    Класс для вазмодействия с API Вконтакте от имени приложения.

    :param token: Токен приложения Вконтакте.
    :param: service_token: Сервисный токен прилонжения Вконтакте
    :param: app_id: Идентификатор приложения вконтакте.
    :param: client_secret: Секретный ключ приложения вконтакте.
    :param: server_url: Адрес сервера OAUTH авторизации.
    :param: api_version: Версия API Вконтакте.
    """
    def __init__(self, token: str,
                 service_token: str,
                 app_id: str,
                 client_secret: str,
                 server_url: str,
                 api_version: str):
        super().__init__(token=token, api_version=api_version)
        self.app_id = app_id
        self.client_secret = client_secret
        self.server_url = server_url
        self.service_token = service_token
