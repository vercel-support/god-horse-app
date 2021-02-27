import json
import time
import pytest

from starlette.testclient import TestClient

from app import create_app
from app.routers.ticket import tickets
from app.config import get_settings

client = TestClient(create_app())
pre_fix = '/api/v1'
settins = get_settings()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


@pytest.mark.flaky(reruns=3, reruns_delay=3)
def test_refresh_tickets():
    response = client.get(
        f'{pre_fix}/refresh?sheet_name=20210227',  headers={'x-api-key': settins.API_KEY.get_secret_value()})
    assert response.status_code == 200
    assert tickets and tickets.get('20210227')


def test_get_img():
    response = client.post(
        f'{pre_fix}/img/20210227/template.png')
    assert response.status_code == 200


def test_get_ticket():
    n_before = len(tickets['20210227'])
    response = client.get(
        f'{pre_fix}/get_ticket?sheet_name=20210227&name=test&email=test@gmail.com',  headers={'x-api-key': settins.API_KEY.get_secret_value()})
    assert response.status_code == 200
    # assert is_number(response.json().get('number'))
    assert len(response.json().get('words')) > 3
    time.sleep(0.5)
    assert n_before - len(tickets['20210227']) == 1
