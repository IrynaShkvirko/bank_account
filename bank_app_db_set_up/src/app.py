import json

from flask import request

from . import create_app, database
from .models import Users
import datetime

app = create_app()

history = {}
account_operations = []


@app.route('/', methods=['GET'])
def fetch_all_users():
    users = database.get_all(Users)
    all_users = []
    for user in users:
        new_user = {
            "id": user.id,
            "balance": user.balance,
            "overdraft": user.overdraft,
        }

        all_users.append(new_user)
    return json.dumps(all_users), 200


@app.route('/add', methods=['POST'])
def add_user():
    data = request.get_json()

    balance = data['balance']
    overdraft = data['overdraft']

    database.add_instance(Users, balance=balance, overdraft=overdraft)
    return json.dumps("Added"), 200


@app.route('/<user>/account/balance', methods=['GET'])
def get_user_balance(user_id):
    users = database.get_all(Users)
    if user_id not in users:
        return "Can't get the balance of current user"
    else:
        current_time = datetime.datetime.now()
        return f"Your account balance is {users['balance']} as of {current_time}"


@app.route('/<user>/account/balance', methods=['PUT'])
def change_user_balance(user_id):
    users = database.get_all(Users)
    amount = request.get_json()['amount']
    if user_id not in users:
        return "You can't deposit or withdraw money for the current user"
    if request.get_json()['operation'].lower() == 'deposit':
        if amount <= 0:
            return "Invalid deposit amount. Amount should be > 0"
        else:
            account_operations.append(set_operation_history())
            new_balance = users['balance'] + amount
            database.edit_instance(Users, id=user_id, balance=new_balance)
            return f"You deposited: {amount} your current balance is: {users['balance']}"
    elif request.get_json()['operation'].lower() == 'withdrawal':
        if amount > users['balance'] and users['overdraft'] == 0:
            return "Can't withdraw beyond the current account balance."
        elif amount <= 0:
            return "Invalid withdraw amount."
        elif users['balance'] < 0 and users['overdraft'] < amount:
            return "You went below the overdraft limit."
        else:
            account_operations.append(set_operation_history())
            new_balance = Users[user_id]['balance'] - amount
            database.edit_instance(Users, id=user_id, balance=new_balance)
            return f"You withdrawn: {amount} your current balance is: {users['balance']}"

    return json.dumps("Edited"), 200


def set_operation_history():
    amount = request.get_json()['amount']
    current_time = datetime.datetime.now()
    if request.get_json()['operation'] == 'deposit':
        history['operation_type'] = 'deposit'
        history['amount'] = amount
    else:
        history['amount'] = -amount
        history['operation_type'] = 'withdrawal'
    history['time'] = str(current_time)
    return history


@app.route('/<user>/account/overdraft', methods=['GET'])
def get_user_overdraft(user_id):
    data = request.get_json()
    overdraft = data['overdraft']
    return f"Overdraft limit on your account is {overdraft}"


@app.route('/<user>/account/overdraft', methods=['POST, PUT'])
def request_overdraft(user_id):
    data = request.get_json()
    if request.method == 'POST':
        overdraft = data['overdraft']
        database.add_instance(Users, id=user_id, overdraft=overdraft)
    elif request.method == 'PUT':
        new_overdraft = data['overdraft']
        database.edit_instance(Users, id=user_id, overdraft=new_overdraft)
    else:
        return "Operation can't be performed"



