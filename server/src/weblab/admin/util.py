import sha
import random

def password2sha(password):
    randomstuff = ""
    for _ in range(4):
        c = chr(ord('a') + random.randint(0, 25))
        randomstuff += c
    password = password if password is not None else ''
    return randomstuff + "{sha}" + sha.new(randomstuff + password).hexdigest()

