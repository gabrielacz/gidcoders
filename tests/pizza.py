import json

import pytest
import requests

url = 'http://127.0.0.1:5000'

from app import app, db


@pytest.fixture
def test_client():
    return app.test_client()


def test_listing_pizza(test_client):
    # WHEN
    r = test_client.get(url + '/list/')
    # THEN
    assert r.status_code == 200
    # assert len(json.loads(r.data).get('pizzas')) == 7 #TODO set db for test


def test_index_page(test_client):
    # WHEN
    r = test_client.post(url + '/vote/', json={"name": "PizzaLove<3"})
    # THEN
    assert r.status_code == 204
    # TODO set db for test
    # r = test_client.get(url + '/list/')
    # assert r.status_code == 200
    # assert len(json.loads(r.data).get('pizzas')) == 8
