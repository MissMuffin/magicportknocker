from appdirs import user_data_dir
import json

appname = "Magic Port Knocker"
appauthor = "MissMuffin"
file_name = user_data_dir(appname, appauthor) + "/state.json"

class State:
    secret = ""
    number_of_remaining_tickets = 0

    def __init__(self, secret, number_of_remaining_tickets):
        self.secret = secret
        self.number_of_remaining_tickets = number_of_remaining_tickets

    def save(self):
        with open(file_name, "w") as f:
            json.dump(self.__dict__, f) # some bullshit to avoid having to serialize this

    @staticmethod
    def read():
        with open(file_name, "r") as f:
            state_dict =  json.load(f)
            return State(state_dict["secret"], state_dict["number_of_remaining_tickets"])