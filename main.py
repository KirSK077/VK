import os
import requests
import time
import datetime
from tqdm import tqdm
import json


class VK:
    """Класс для получений информации о фотографиях из профиля ВК."""
    def __init__(self, vk_id_file, vk_token_file, version='5.131'):
        self.vk_id = vk_id_file
        self.vk_token = vk_token_file
        self.version = version
        self.params = {}


    def get_vk_token(self):
        vk_token_path = os.path.join(os.getcwd(), self.vk_token)
        with open(vk_token_path, 'r', encoding='utf-8') as text:
            self.vk_token = text.read()
            return self.vk_token

    def get_vk_id(self):
        vk_id_path = os.path.join(os.getcwd(), self.vk_id)
        with open(vk_id_path, 'r', encoding='utf-8') as text:
            self.vk_id = text.read()
            return self.vk_id

    def get_user_photo(self, album, offset, count):
        """Получение словаря в формате 'Название фото: [ссылка, типоразмер файла]' для дальнейшего использования и
        загрузки на ЯндексДиск.
        Название фото формируется в соответствии с требованиями к оформлению курсовой работы:
        'Название фото': 'количество лайков(суммарное пользователя и посетителей)__дата_время загрузки в ВК'."""
        url = 'https://api.vk.com/method/photos.get'
        self.params = {
            'access_token': self.get_vk_token(),
            'owner_id': self.get_vk_id(),
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

    def get_json_file(self, json_file):
        """Получение json-файла с информацией по загруженным изображениям в формате:
        [{"file_name": "Название фото", "size": "размер фото"}]."""
        json_list = []
        for key, val in self.dict_photos.items():
            json_list.append({'file name': f'{key}', 'size': val[1]})
        path = os.path.join(os.getcwd(), json_file)
        with open(path, 'w') as write_file:
            json.dump(json_list, write_file, ensure_ascii=False, indent=2)
        return path


class YandexDisk(VK):
    """Класс для загрузки изображений, полученных с помощью класса VK, на ЯндексДиск."""
    def __init__(self, yd_token_file, yd_folder_path):
        self.yd_token_file = yd_token_file
        self.yd_folder_path = yd_folder_path
        self.headers = {}
        super().__init__(self, VK)
        self.dict_photos = VK.dict_photos

    def get_yd_token(self):
        token_path = os.path.join(os.getcwd(), self.yd_token_file)
        with open(token_path, 'r', encoding='utf-8') as token_text:
            self.yd_token = token_text.read()
            return self.yd_token

    def get_headers(self):
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'OAuth {self.get_yd_token()}'}
        return self.headers

    def create_yd_upload_folder(self):
        """Метод класса YandexDisk для создания папки на ЯндексДиск."""
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        param = {"path": self.yd_folder_path}
        upload_link = requests.put(url=url, params=param, headers=self.get_headers())
        if upload_link.status_code == 201:
            print(f'Папка "{self.yd_folder_path}" успешно создана')

    def upload_photos(self):
        """Метод для загрузки фотографий на ЯндексДиск."""
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        lst_upload_links = []
        for key, val in self.dict_photos.items():
            param = {'path': f'{self.yd_folder_path}/{str(key)}', 'url': f'{val[0]}'}
            lst_upload_links.append(requests.post(url=url, params=param, headers=self.get_headers()))
        for response in tqdm(lst_upload_links, desc='Фотографии', unit=' ед.'):
            response.json().get('href')
            if response.status_code != 202:
                return f'Ошибка при скачивании файла: {response.status_code}'
            time.sleep(0.2)
        return 'Загрузка завершена'


if __name__ == '__main__':
    vk_token = 'vk_token.txt'
    vk_id = 'vk_id.txt'
    album = 'profile'
    offset = 0
    count = 5
    yd_token = 'yd_token.txt'
    yd_folder = 'VK profile photo'
    json_file = 'Json_file.json'
    VK(vk_id, vk_token).get_user_photo(album, offset, count)
    VK(vk_id, vk_token).get_json_file(json_file)
    YandexDisk(yd_token, yd_folder).create_yd_upload_folder()
    print(YandexDisk(yd_token, yd_folder).upload_photos())
