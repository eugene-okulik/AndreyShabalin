import logging

import requests
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import pytest

base_url = "https://api.restful-api.dev"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

data = None


def is_within_one_minute(date_str):
    # Парсинг строки даты в объект datetime с временной зоной
    target_date = parser.isoparse(date_str)

    # Получение текущей даты и времени в UTC
    utc_zone = pytz.utc
    current_date = datetime.now(utc_zone)

    # Разница между целевой датой и текущей датой
    delta = current_date - target_date

    # Проверка, что разница не превышает одну минуту
    if abs(delta) <= timedelta(minutes=1):
        return True
    else:
        return False


def test_get_all_objects():
    """
    Получаем все объекты
    :return: json со всеми объектами, каждый из которых содержит:
    id    - id объекта
    name  - Наименование объекта
    data  - Вложенный json, который содержит:
    color - Цвет объекта
    capacity GB - Размер памяти объекта
    """
    result = requests.get(f"{base_url}/objects")
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert len(result_body) > 1, \
        logging.error("Количество записей меньше или равно одной")


def test_get_objects_by_id():
    """
    Получаем объекты по их id-шникам
    :return: json с объектами, каждый из которых содержит:
    id    - id объекта
    name  - Наименование объекта
    data  - Вложенный json, который содержит:
    color - Цвет объекта
    capacity GB - Размер памяти объекта
    """
    test_ids = ["1", "3"]
    result = requests.get(f"{base_url}/objects?id={test_ids[0]}&id={test_ids[1]}")
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body[0]['id'] == test_ids[0] and result_body[1]['id'] == test_ids[1], \
        logging.error("Получили неверную запись, либо их порядок не соответствует требованиям")


def test_get_object_by_id():
    """
    Получаем один объект по его id-шнику
    :return: json с объектом, каждый из которых содержит:
    id    - id объекта
    name  - Наименование объекта
    data  - Вложенный json, который содержит:
    color - Цвет объекта
    capacity GB - Размер памяти объекта
    """
    test_id = "1"
    result = requests.get(f"{base_url}/objects/{test_id}")
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body['id'] == test_id, \
        logging.error("Получили неверную запись")


def test_add_object():
    """
    Создаём один объект
    :body: json с информацией об объекту (аналогичной как в return, только без id)
    :return: json с объектом, каждый из которых содержит:
    id    - id объекта
    name  - Наименование объекта
    data  - Вложенный json, который содержит:
    color - Цвет объекта
    capacity GB - Размер памяти объекта
    """
    test_body = {
        "name": "Apple MacBook Pro 19",
        "data": {
            "year": 2019,
            "price": 1849.99,
            "CPU model": "Intel Core i9",
            "Hard disk size": "1 TB"
        }
    }
    result = requests.post(f"{base_url}/objects", json=test_body)
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body['id'] is not None and is_within_one_minute(result_body['createdAt']), \
        logging.error("Запись создалась не корректно")
    return result_body['id']


@pytest.fixture(scope="module")
def create_object():
    return test_add_object()


def test_update_all_object(create_object):
    """
    Обновляем один объект
    :body: json с информацией об объекту (аналогичной как в return, только без id)
    :return: json с объектом, каждый из которых содержит:
    id    - id объекта
    name  - Наименование объекта
    data  - Вложенный json, который содержит:
    color - Цвет объекта
    capacity GB - Размер памяти объекта
    """
    test_id = create_object
    test_body = {
        "name": "Samsung MacBook Pro 19",
        "data": {
            "year": 3019,
            "price": 1849.99,
            "CPU model": "Intel Core i99",
            "Hard disk size": "3 TB"
        }
    }
    result = requests.put(f"{base_url}/objects/{test_id}", json=test_body)
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body['id'] == test_id \
           and result_body["name"] == test_body["name"] \
           and result_body["data"] == test_body["data"] \
           and is_within_one_minute(result_body['updatedAt']), \
        logging.error("Запись обновилась не корректно")
    return result_body['id']


def test_update_partially_object(create_object):
    """
    Частично обновляем один объект
    :body: json с информацией об объекту (аналогичной как в return, только без id)
    :return: json с объектом, каждый из которых содержит:
    id    - id объекта
    name  - Наименование объекта
    data  - Вложенный json, который содержит:
    color - Цвет объекта
    capacity GB - Размер памяти объекта
    """
    test_id = create_object
    test_body = {
        "name": "Xiaomi MacBook Pro 19"
    }
    result = requests.patch(f"{base_url}/objects/{test_id}", json=test_body)
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body['id'] == test_id \
           and result_body['name'] == test_body['name'] \
           and is_within_one_minute(result_body['updatedAt']), \
        logging.error("Запись обновилась не корректно")


def test_delete_object_by_id(create_object):
    """
    Удаляем один объект по его id-шнику
    :return: сообщение об успешном удалении объекта
    """
    test_id = create_object
    result = requests.delete(f"{base_url}/objects/{test_id}")
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body['message'] == f"Object with id = {test_id} has been deleted.", \
        logging.error("Удалили неверную запись")
