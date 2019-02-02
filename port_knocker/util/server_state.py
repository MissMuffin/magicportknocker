import os
import json
from base64 import b64encode, b64decode
from pathlib2 import Path
from .auth import generate_secret, generate_nth_ticket


auth_port = "10000"
server_ip = "localhost"

class ServerStateUser():
    user_id = 0
    user_name = ""
    n_tickets = 0
    secret = b"SECRET"
    symm_key = b"SYMM_KEY"
    ports = []

    def __init__(self, user_id, user_name, ports, n_tickets=10,
                 secret=None, symm_key=None):
        self.user_id = user_id
        self.user_name = user_name
        self.n_tickets = n_tickets
        self.ports = ports

        self.secret = secret
        if secret == None:
            self.secret = generate_secret()
        
        self.symm_key = symm_key
        if symm_key == None:
            self.symm_key = generate_secret()
        
    def get_dict(self):
        # get dict for saving as json serverside
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "n_tickets": self.n_tickets,
                "secret": b64encode(generate_nth_ticket(self.secret, self.n_tickets + 1)).decode(),
                "symm_key":b64encode(self.symm_key).decode(),
                "ports": self.ports}

    def get_client_setup_dict(self):
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "n_tickets": self.n_tickets,
                "secret": b64encode(self.secret).decode(),
                "symm_key":b64encode(self.symm_key).decode(),
                "ports": self.ports}

    def generate_client_setup_file(self):
        # check if dir for user exists
        cwd = os.getcwd()
        folder_path = cwd + "/user_setups/{}_{}".format(self.user_id, self.user_name)
        Path(folder_path).mkdir(exist_ok=True) #TODO escape name?
        # build file path
        setup_file = folder_path + "/save_file.json"
        # create dict with setup data to be saved to json
        setup = {}
        setup["user"] = self.get_client_setup_dict()
        setup["server_ip"] = server_ip
        setup["auth_port"] = auth_port
        # write to file
        with open(setup_file, "w+") as f:
            json.dump(setup, f)


class ServerState():
    id_count = 0
    users = []
    _save_file = "server_state.json"

    def __init__(self, id_count=0, users=None, save_file="server_state.json"):
        self.id_count = id_count
        self.server_ip = server_ip
        self.auth_port = auth_port

        # needs to be None in function head: https://stackoverflow.com/questions/4535667/python-list-should-be-empty-on-class-instance-initialisation-but-its-not-why
        if users == None:
            self.users = []
        else:
            self.users = users
        self._save_file = save_file
        # self.save()

    #  saves user id count and user data to json
    def save(self):
        state = {}
        state["id_count"] = self.id_count
        state["users"] = []
        for user in self.users:
            state["users"].append(user.get_dict())
        with open(self._save_file, "w+") as f:
            json.dump(state, f)

    # loads user id count and user data from json
    def load(self):
        with open(self._save_file, "r") as f:
            state_dict = json.load(f)
            for user in state_dict["users"]:
                self.users.append(ServerStateUser(user_id=user["user_id"],
                                                  user_name=user["user_name"],
                                                  n_tickets=user["n_tickets"],
                                                  secret=b64decode(user["secret"]),
                                                  symm_key=b64decode(user["symm_key"]),
                                                  ports=user["ports"]))
            self.id_count = state_dict["id_count"]

    #  adds new user and saves new user to json
    def add_user(self, user_name, n_tickets, ports):
        new_user = ServerStateUser(user_id=self.id_count,
                                   user_name=user_name,
                                   n_tickets=n_tickets,
                                   ports=ports)
        self.users.append(new_user)
        self.id_count += 1
        new_user.generate_client_setup_file()
        self.save() 

    def get_user(self, user_id):
        for i, user in enumerate(self.users):
            if user.user_id == user_id:
                return self.users[i]
        return None

    def remove_user_by_id(self, user_id):
        for i, user in enumerate(self.users):
            if user.user_id == user_id:
                self.users.pop(i)
                self.save()
                return user
            else:
                return "No user with that id."

    def remove_all_users(self):
        self.id_count = 0
        del self.users
        self.users = []
        self.save()

    def generate_all_client_setup_files(self):
        for user in self.users:
            user.generate_client_setup_file()
