from appdirs import user_data_dir
import json
import os

appname = "Magic Port Knocker"
appauthor = "MissMuffin"
appdir = user_data_dir(appname, appauthor)
file_name = appdir + "/state.json"

class State:
    secret = ""
    number_of_remaining_tickets = 0

    def __init__(self, secret, number_of_remaining_tickets):
        self.secret = secret
        self.number_of_remaining_tickets = number_of_remaining_tickets

    def save(self):
        try:
            os.makedirs(appdir)
        except FileExistsError:
            pass
            
        with open(file_name, "w") as f:
            json.dump(self.__dict__, f) # some bullshit to avoid having to serialize this

    @staticmethod
    def load():
        with open(file_name, "r") as f:
            state_dict =  json.load(f)
            return State(state_dict["secret"], state_dict["number_of_remaining_tickets"])