import pymongo
import bcrypt


def clean_inputs(message: str):
    clean_output = ""
    for i in message:
        if i == "<":
            clean_output += "&lt"
        elif i == ">":
            clean_output += "&gt"
        elif i == "&":
            clean_output += "&amp"
        else:
            clean_output += i
    return clean_output

def create_account(username, password):
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(password.encode(),salt)
    build_entry = {'username': username, 'password': hash_password}
    return build_entry