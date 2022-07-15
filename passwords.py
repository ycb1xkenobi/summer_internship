import random


def create_password():
    password = ''
    for x in range(16):
        password = password + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))
    return password
