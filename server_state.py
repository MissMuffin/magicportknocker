import os
import json


class ServerStateUser():
    user_id = 0
    user_name = ""
    n_tickets = 0
    secret = "SECRET"
    symm_key = "SYMM_KEY"
    ports = []

    def __init__(self, user_id, user_name, ports, n_tickets=10,
                 secret=None, symm_key=None):
        self.user_id = user_id
        self.user_name = user_name
        self.n_tickets = n_tickets
        self.ports = ports

        if secret == None:
            # TODO generate secret
            self.secret = "SECRET"
        else:
            self.secret = secret

        if symm_key == None:
            # TODO generate secret
            self.symm_key = "SYMM_KEY"
        else:
            self.symm_key = symm_key

    # get dict for saving as json serverside
    def get_dict(self):
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "n_tickets": self.n_tickets,
                "secret": self.secret, #should be nth ticket
                "symm_key":self.symm_key,
                "ports": self.ports}

    def get_client_setup_dict(self):
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "n_tickets": self.n_tickets,
                "secret": self.secret,
                "symm_key":self.symm_key,
                "ports": self.ports}

    def generate_client_setup_file(self):
        setup_file = "client_setup_{}_{}.json".format(
            self.user_id, self.user_name)
        with open(setup_file, "w+") as f:
            json.dump(self.get_client_setup_dict(), f)


class ServerState():
    id_count = 0
    users = []
    _save_file = "server_state.json"

    def __init__(self, id_count=0, users=None, save_file="server_state.json"):
        self.id_count = id_count

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
            # state["users"].append(user.__dict__)  # .get_dict()
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
                                                  secret=user["secret"],
                                                  symm_key=user["symm_key"],
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
