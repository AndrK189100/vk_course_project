import vk_api

class CpVkApi(vk_api.VkApi):
    def __init__(self, token: str, app_id: str, client_secret: str, server_url: str):
        super().__init__(token=token)
        self.app_id = app_id
        self.client_secret = client_secret
        self.server_url = server_url


