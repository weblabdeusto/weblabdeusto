import sha
import random
from flask import Markup

def password2sha(password, randomstuff = None):
    if randomstuff is None:
        randomstuff = ""
        for _ in range(4):
            c = chr(ord('a') + random.randint(0, 25))
            randomstuff += c
    password = password if password is not None else ''
    return randomstuff + "{sha}" + sha.new(randomstuff + password).hexdigest()

def display_date(date):
    if date is not None:
        formatted_date = date.strftime("%Y-%m-%d %H:%M:%SZ")
        return Markup("<span data-date='{date}'>{date}</span>".format(date=formatted_date))
    else:
        return ""
