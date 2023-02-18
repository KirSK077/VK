import requests
import time
from tqdm import tqdm
from VK_photo_get import VK


class YD:
    """Класс для загрузки изображений, полученных с помощью класса VK, на ЯндексДиск."""
    def __init__(self, yd_token, yd_folder_path):
        self.yd_token = yd_token
        self.yd_folder_path = yd_folder_path
        self.headers = {}
        self.dict_photos = VK.dict_photos

    def get_headers(self):
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'OAuth {self.yd_token}'}
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
