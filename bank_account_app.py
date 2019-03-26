from flask import Flask, request
import datetime


app = Flask('BigBankInc')

# Registered users. Keys - users, values - accounts

USERS = {
    'user_1': {'balance': 100, 'overdraft': 0},
    'user_2': {'balance': -200, 'overdraft': 50},
    'user_3': {'balance': 300, 'overdraft': 100},
    'user_4': {'balance': -50, 'overdraft': 100},
}
history = {}
account_operations = []


@app.route('/<user>/account', methods=['GET'])
def user_account(user):
    if user in USERS.keys():
        return f"Your account balance is: {USERS[user]['balance']} . Your current overdraft is: {USERS[user]['overdraft']}" \
            f" Operations performed on your account {account_operations}"
    else:
        return "User does not exist. Please proceed with the registration"


@app.route('/<user>/account/balance', methods=['GET'])
def get_user_balance(user):
    if user in USERS.keys():
        current_time = datetime.datetime.now()
        return f"Your account balance is {USERS[user]['balance']} as of {current_time}"
    else:
        return "Can't get the balance of current user"


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


@app.route('/<user>/account/balance', methods=['PUT'])
def change_user_balance(user):
    amount = request.get_json()['amount']
    if user not in USERS:
        return "You can't deposit or withdraw money for the current user"
    if request.get_json()['operation'].lower() == 'deposit':
        if amount <= 0:
            return "Invalid deposit amount. Amount should be > 0"
        else:
            account_operations.append(set_operation_history())
            USERS[user]['balance'] += amount
            return f"You deposited: {amount} your current balance is: {USERS[user]['balance']}"
    elif request.get_json()['operation'].lower() == 'withdrawal':
        if amount > USERS[user]['balance'] and USERS[user]['overdraft'] == 0:
            return "Can't withdraw beyond the current account balance."
        elif amount <= 0:
            return "Invalid withdraw amount."
        elif USERS[user]['balance'] < 0 and USERS[user]['overdraft'] < amount:
            return "You went below the overdraft limit."
        else:
            account_operations.append(set_operation_history())
            USERS[user]['balance'] -= amount
            return f"You withdrawn: {amount} your current balance is: {USERS[user]['balance']}"


@app.route('/<user>/account/overdraft', methods=['GET'])
def get_user_overdraft_status(user):
    return f"Overdraft limit on your account is {USERS[user]['overdraft']}"


@app.route('/<user>/account/overdraft', methods=['POST'])
def request_overdraft(user):
    USERS[user]['overdraft'] = request.get_json()['amount']
    return f"The overdraft was set to {USERS[user]['overdraft']}"


@app.route('/<user>/account/overdraft', methods=['DELETE'])
def cancel_overdraft(user):
    if USERS[user]['balance'] < 0:
        return "To cancel the overdraft it has to be paid off first."
    else:
        USERS[user]['overdraft'] = 0
