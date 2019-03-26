from flask import Flask, request

app = Flask('BigBankInc')

# Registered users. Keys - users, values - accounts

USERS = {
    'user_1': {'balance': 100, 'overdraft': 0},
    'user_2': {'balance': 200, 'overdraft': 50},
    'user_3': {'balance': 300, 'overdraft': 100},
}


@app.route('/<user>/account', methods=['HEAD', 'GET'])
def user_account(user):
    if request.method == 'HEAD':
        return user in USERS.keys()
    elif request.method == 'GET':
        return USERS[user]


@app.route('/<user>/account/balance', methods=['GET'])
def get_user_balance(user):
    return USERS[user]['balance']


@app.route('/<user>/account/balance', methods=['POST'])
def change_user_balance(user):
    if request.get_json()['operation'] == 'deposit':
        USERS[user]['balance'] += request.get_json()['operation']['amount']
    elif request.get_json()['operation'] == 'withdrawal':
        USERS[user]['balance'] -= request.get_json()['operation']['amount']


@app.route('/<user>/account/overdraft', methods=['GET'])
def get_user_overdraft_status(user):
    return USERS[user]['overdraft']


@app.route('/<user>/account/overdraft', methods=['POST'])
def request_overdraft(user):
    USERS[user]['overdraft'] = request.get_json()['amount']


@app.route('/<user>/account/overdraft', methods=['DELETE'])
def cancel_overdraft(user):
    USERS[user]['overdraft'] = 0