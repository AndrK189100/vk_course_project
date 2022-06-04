import random
import vk_api


def check_country(country: str, token: str, api_version='5.131'):
    api = vk_api.VkApi(token=token, api_version=api_version).get_api()
    countries = api.database.getCountries(need_all=1, count=240)
    cap_country = country.capitalize()
    for item in countries['items']:
        if item['title'] == cap_country:
            return item
    return False


def check_city(country: int, city: str, token: str, api_version='5.131') -> bool:
    api = vk_api.VkApi(token=token, api_version=api_version).get_api()
    city = api.database.getCities(q=city, country_id=country, need_all=1)
    if city['count'] > 0:
        return city['items']
    else:
        return False


def get_random_id():
    return random.getrandbits(31) * random.choice([-1, 1])
