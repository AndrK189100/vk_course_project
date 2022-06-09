import vk_api


class CpVkApi(vk_api.VkApi):
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
