import json
import os
import shutil
from base64 import b64decode, b64encode

import appdirs
from pathlib2 import Path

from port_knocker.config.config import Config

from .auth import generate_nth_ticket, generate_secret


class ServerStateUser():
    user_id = 0
    user_name = ""
    n_tickets = 0
    secret = b"SECRET"
    ticket = b"TICKET"
    symm_key = b"SYMM_KEY"
    ports = []

    def __init__(self, user_id, user_name, ports, n_tickets=0,
                symm_key=None, ticket=None):

        self.user_id = user_id
        self.user_name = user_name
        self.n_tickets = n_tickets
        self.ports = ports

        self.ticket = ticket
        if self.ticket == None:
            self.secret = generate_secret()
            self.ticket = generate_nth_ticket(self.secret, self.n_tickets + 1)
        
        self.symm_key = symm_key
        if self.symm_key == None:
            self.symm_key = generate_secret()
        
    def get_dict(self):
        # get dict for saving as json serverside
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "ticket": b64encode(self.ticket).decode(),
                "symm_key":b64encode(self.symm_key).decode(),
                "ports": self.ports}

    def get_client_setup_dict(self):
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "n_tickets": self.n_tickets,
                "secret": b64encode(self.secret).decode(),
                "symm_key":b64encode(self.symm_key).decode(),
                "ports": self.ports}

    def generate_client_setup_file(self, server_ip, auth_port, fname=None):

        if not fname:
            cwd = os.getcwd()
            folder_path = cwd + "/user_setups/{}_{}".format(self.user_name, self.user_id)
            Path(folder_path).mkdir(exist_ok=True, parents=True)
            setup_file = folder_path + "/setup_file.json"
        else:
            setup_file = fname

        setup = {}
        setup["user"] = self.get_client_setup_dict()
        setup["server_ip"] = server_ip
        setup["auth_port"] = str(auth_port)
        with open(setup_file, "w+") as f:
            json.dump(setup, f, indent=4)


class ServerState():

    _savedir = appdirs.user_data_dir(Config.APPNAME, Config.APPAUTHOR)
    _savefile = _savedir + "/server_state.json"
    
    id_count = 0
    users = []
    auth_port = ""
    server_ip = ""

    def __init__(self, server_ip="", auth_port="", id_count=0, users=None, _savefile=None):
        self.id_count = id_count
        self.server_ip = server_ip
        self.auth_port = auth_port

        # list [] needs to be None in function head: 
        # https://stackoverflow.com/questions/4535667/python-list-should-be-empty-on-class-instance-initialisation-but-its-not-why
        if users == None:
            self.users = []
        else:
            self.users = users

        if _savefile != None:
            self._savefile = _savefile

    def save(self):
        Path(self._savedir).mkdir(exist_ok=True, parents=True)
        state = {}
        state["id_count"] = self.id_count
        state["users"] = []
        for user in self.users:
            state["users"].append(user.get_dict())
        state["server_ip"] = self.server_ip
        state["auth_port"] = str(self.auth_port)
        with open(self._savefile, "w+") as f:
            json.dump(state, f, indent=4)

    def load(self):
        with open(self._savefile, "r") as f:
            state_dict = json.load(f)
            for user in state_dict["users"]:
                self.users.append(ServerStateUser(user_id=user["user_id"],
                                                  user_name=user["user_name"],
                                                  ticket=b64decode(user["ticket"]),
                                                  symm_key=b64decode(user["symm_key"]),
                                                  ports=user["ports"]))
            self.id_count = state_dict["id_count"]
            self.server_ip = state_dict["server_ip"]
            self.auth_port = int(state_dict["auth_port"])

    def add_user(self, user_name, n_tickets, ports, fname=None):
        new_user = ServerStateUser(user_id=self.id_count,
                                   user_name=user_name,
                                   n_tickets=n_tickets,
                                   ports=ports)
        self.users.append(new_user)
        self.id_count += 1
        new_user.generate_client_setup_file(self.server_ip, self.auth_port, fname=fname)
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
                self.remove_user_setup(user.user_id, user.user_name)
                return user
            else:
                return "No user with that id."

    def remove_user_setup(self, user_id, user_name):
        cwd = os.getcwd()
        file_path = cwd + "/user_setups/{}_{}".format(user_name, user_id)
        shutil.rmtree(file_path, ignore_errors=True)

    def remove_all_user_setups(self):
        for user in self.users:
            self.remove_user_setup(user.user_id, user.user_name)

    def remove_all_users(self):
        self.remove_all_user_setups()
        self.id_count = 0
        del self.users
        self.users = []
        self.save()

    def generate_all_client_setup_files(self):
        for user in self.users:
            user.generate_client_setup_file(self.server_ip, self.auth_port)

    def update_user(self, id, new_ports=None, new_symm_key=None):
        user = self.get_user(id)
        user.ports = new_ports
        user.symm_key = new_symm_key
        user.generate_client_setup_file(self.server_ip, self.auth_port)
        self.save()
