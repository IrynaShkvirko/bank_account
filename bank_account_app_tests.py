import pytest
import json
from bank_account_app import app


@pytest.fixture
def client():
    test_client = app.test_client()
    return test_client


def test_non_existing_user_account(client):
    response = client.get("/user_6/account")
    assert response.status_code == 200
    assert response.data.decode() == 'User does not exist. Please proceed with the registration'


def test_balance_of_existing_user(client):
    response = client.get("/user_1/account/balance")
    assert response.status_code == 200
    assert int(response.data.decode()) == 100  # balance


def test_balance_of_non_existing_user(client):
    response = client.get("/user_6/account/balance")
    assert response.status_code == 200
    assert response.data.decode() == 'Can\'t get the balance of current user'


def test_deposit_operation(client):
    response = client.post('/user_1/account/balance', data=json.dumps({'operation': 'deposit', 'amount': 200}),
                           content_type='application/json')
    assert response.status_code == 200
    assert int(response.data.decode()) == 300  # balance


def test_insufficient_deposit_operation(client):
    response = client.post('/user_1/account/balance', data=json.dumps({'operation': 'deposit', 'amount': 0}),
                           content_type='application/json')
    assert response.status_code == 200
    assert response.data.decode() == 'Invalid deposit amount. Amount should be > 0'


def test_withdrawal_operation(client):
    response = client.post('/user_1/account/balance', data=json.dumps({'operation': 'withdrawal', 'amount': 30}),
                           content_type='application/json')
    assert response.status_code == 200
    assert int(response.data.decode()) == 70  # balance


def test_withdrawal_operation_beyond_balance(client):
    response = client.post('/user_1/account/balance', data=json.dumps({'operation': 'withdrawal', 'amount': 200}),
                           content_type='application/json')
    assert response.status_code == 200
    assert response.dataresponse.data.decode() == 'Can\'t withdraw beyond the current account balance.'


def test_withdrawal_operation_beyond_overdraft(client):
    response = client.post('/user_1/account/balance', data=json.dumps({'operation': 'withdrawal', 'amount': -50}),
                           content_type='application/json')
    assert response.status_code == 200
    assert response.data.decode() == 'Invalid withdraw amount.'


def test_insufficient_withdrawal_operation(client):
    response = client.post('/user_2/account/balance', data=json.dumps({'operation': 'withdrawal', 'amount': 100}),
                          content_type='application/json')
    assert response.status_code == 200
    assert response.data.decode() == 'You went below the overdraft limit.'


def test_user_account_overdraft(client):
    response = client.get('/user_3/account/overdraft')
    assert response.status_code == 200
    assert int(response.data.decode()) == 100


def test_overdraft_set_up(client):
    response = client.post('/user_3/account/overdraft', data=json.dumps({'amount': 50}),
                           content_type='application/json')
    assert response.status_code == 200
    assert int(response.data.decode()) == 50


def test_overdraft_canceling(client):
    response = client.delete('/user_3/account/overdraft')
    assert response.status_code == 200
    assert int(response.data.decode()) == 0


def test_overdraft_canceling_on_active_debt(client):
    response = client.delete('/user_4/account/overdraft')
    assert response.status_code == 200
    assert response.data.decode() == 'To cancel the overdraft it has to be paid off first.'
