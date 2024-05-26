import logging

import requests
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import pytest

# pytest -s -v homework/andrey_shabalin/hw18

base_url = "https://api.restful-api.dev"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

data = None

test_body = {
    "name": "Apple MacBook Pro 19",
    "data": {
        "year": 2019,
        "price": 1849.99,
        "CPU model": "Intel Core i9",
        "Hard disk size": "1 TB"
    }
}

test_body_2 = {
    "name": "LG TV PC CONSOLE 4 in 1",
    "data": {
        "year": 2019,
        "price": 1849.99,
        "CPU model": "Intel Core i9",
        "Hard disk size": "1 TB"
    }
}

test_body_3 = {
    "name": "Lenovo ThinkPad",
    "data": {
        "year": 2019,
        "price": 1849.99,
        "CPU model": "Intel Core i9",
        "Hard disk size": "1 TB"
    }
}

test_bodies = [test_body, test_body_2, test_body_3]


@pytest.fixture(scope="package", autouse=True)
def module_fixture():
    print("\nStart testing\n")
    yield
    print("Testing completed\n")


@pytest.fixture(scope="module")
def create_object():
    return add_object(test_body)


@pytest.fixture(scope="function", autouse=True)
def function_fixture():
    print("\nbefore test\n")
    yield
    print("\nafter test")


def add_object(created_body):
    result = requests.post(f"{base_url}/objects", json=created_body)
    return result


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
    """
    result = requests.get(f"{base_url}/objects")
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert len(result_body) > 1, \
        logging.error("Количество записей меньше или равно одной")


def test_get_objects_by_id():
    """
    Получаем объекты по их id-шникам
    """
    test_ids = ["1", "3"]
    result = requests.get(f"{base_url}/objects?id={test_ids[0]}&id={test_ids[1]}")
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body[0]['id'] == test_ids[0] and result_body[1]['id'] == test_ids[1], \
        logging.error("Получили неверную запись, либо их порядок не соответствует требованиям")


def test_get_object_by_id(create_object):
    """
    Получаем один объект по его id-шнику
    """
    test_id = create_object.json()["id"]
    result = requests.get(f"{base_url}/objects/{test_id}")
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body['id'] == test_id, \
        logging.error("Получили неверную запись")


@pytest.mark.critical
@pytest.mark.parametrize("test_body", test_bodies)
def test_add_object(test_body):
    """
    Создаём один объект
    """
    result = add_object(test_body)
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body['id'] is not None and is_within_one_minute(result_body['createdAt']), \
        logging.error("Запись создалась не корректно")


@pytest.mark.medium
def test_update_all_object(create_object):
    """
    Обновляем один объект
    """
    test_id = create_object.json()["id"]
    updated_test_body = {
        "name": "Samsung MacBook Pro 19",
        "data": {
            "year": 3019,
            "price": 1849.99,
            "CPU model": "Intel Core i99",
            "Hard disk size": "3 TB"
        }
    }
    result = requests.put(f"{base_url}/objects/{test_id}", json=updated_test_body)
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body['id'] == test_id \
            assert result_body["name"] == updated_test_body["name"], logging.error("Имена записей не совпадают")
    assert result_body["data"] == updated_test_body["data"], logging.error("Данные записей не совпадают")
    assert is_within_one_minute(result_body['updatedAt']), logging.error(
        "Время записей не совпадает или имеет разницу больше минуты")


def test_update_partially_object(create_object):
    """
    Частично обновляем один объект
    """
    test_id = create_object.json()["id"]
    test_body = {
        "name": "Xiaomi MacBook Pro 19"
    }
    result = requests.patch(f"{base_url}/objects/{test_id}", json=test_body)
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body['id'] == test_id, logging.error("ID записей не совпадают")
    assert result_body['name'] == test_body['name'], logging.error("Name записей не совпадают")
    assert is_within_one_minute(result_body['updatedAt']), logging.error("Время записей не совпадает или отличается "
                                                                         "больше чем на минуту")


def test_delete_object_by_id(create_object):
    """
    Удаляем один объект по его id-шнику
    """
    test_id = create_object.json()["id"]
    result = requests.delete(f"{base_url}/objects/{test_id}")
    assert result.status_code == 200, logging.error(f"Статус код равен {result.status_code}")
    result_body = result.json()
    assert result_body['message'] == f"Object with id = {test_id} has been deleted.", \
        logging.error("Удалили неверную запись")
