from VK_photo_get import VK
from YD_upload_photo import YD
import os
import json


def get_json_file(json_filename, dict_photos):
    """Получение json-файла с информацией по загруженным изображениям в формате:
    [{"file_name": "Название фото", "size": "размер фото"}]."""
    json_list = []
    for key, val in dict_photos.items():
        json_list.append({'file name': f'{key}', 'size': val[1]})
    path = os.path.join(os.getcwd(), json_filename)
    with open(path, 'w') as write_file:
        json.dump(json_list, write_file, ensure_ascii=False, indent=2)
    return path


vk_token = 'vk_token.txt'
vk_id = input('Введите id Вашего профиля Вконтакте: \n').strip()[2:]
album = 'profile'
offset = 0
count = int(input('Введите количество фотографий, которые необходимо скачать: \n'))
yd_token = input('Введите токен Яндекс.Диска: \n').strip()
yd_folder = input('Введите название папки для загрузки изображений: \n')
json_file = 'Json_file.json'

VK(vk_id, vk_token).get_user_photo(album, offset, count)
get_json_file(json_file, VK.dict_photos)
YD(yd_token, yd_folder).create_yd_upload_folder()
print(YD(yd_token, yd_folder).upload_photos())
