import os
import requests
import time
import datetime


class VK:
    """Класс для получений информации о фотографиях из профиля ВК."""
    def __init__(self, vk_id, vk_token_file, version='5.131'):
        self.vk_id = vk_id
        self.vk_token = vk_token_file
        self.version = version
        self.params = {}

    def get_vk_token(self):
        vk_token_path = os.path.join(os.getcwd(), self.vk_token)
        with open(vk_token_path, 'r', encoding='utf-8') as text:
            self.vk_token = text.read()
            return self.vk_token

    def get_user_photo(self, album, offset, count):
        """Получение словаря в формате 'Название фото: [ссылка, типоразмер файла]' для дальнейшего использования и
        загрузки на ЯндексДиск.
        Название фото формируется в соответствии с требованиями к оформлению курсовой работы:
        'Название фото': 'количество лайков(суммарное пользователя и посетителей)__дата_время загрузки в ВК'."""

        url = 'https://api.vk.com/method/photos.get'
        self.params = {
            'access_token': self.get_vk_token(),
            'owner_id': self.vk_id,
            'album_id': album,
            'extended': 1,
            'offset': offset,
            'count': count,
            'v': self.version
        }
        res = requests.get(url, params=self.params)
        photo_sizes_vk = ['s', 'm', 'x', 'o', 'p', 'q', 'r', 'y', 'z',
                          'w']  # список типовых размеров изображений с сортировкой по возрастанию размера
        lst_sizes = [[size['type'] for size in res.json()['response']['items'][el]['sizes']]
                     for el in range(len(res.json()['response']['items']))]  # список размеров изображений из ВК
        lst_index = [[photo_sizes_vk.index(i) for i in el].index(max([photo_sizes_vk.index(i) for i in el]))
                     for el in lst_sizes]  # список индексов для получения ссылок на изображения

        VK.dict_photos = {
                f"{sum(res.json()['response']['items'][photo]['likes'].values())}__"
                f"{(datetime.datetime.strptime(time.ctime(res.json()['response']['items'][photo]['date']), '%a %b %d %H:%M:%S %Y')).strftime('%d-%m-%Y_%H-%M-%S')}.jpg":
                [res.json()['response']['items'][photo]['sizes'][lst_index[photo]]['url'],
                 res.json()['response']['items'][photo]['sizes'][lst_index[photo]]['type']]
                for photo in range(len(res.json()['response']['items']))
        }
        if count > len(res.json()['response']['items']):
            print(f"Количество запрашиваемых фото больше, чем содержится в альбоме. "
                  f"Будет загружено максимальное кол-во фото в альбоме ({len(res.json()['response']['items'])} фото)")
        return VK.dict_photos
