import os
import json


class ServerStateUser():
    user_id = 0
    user_name = ""
    number_of_tickets = 0
    verification_key = "SECRET"
    ports = []

    def __init__(self, user_id, user_name, ports, number_of_tickets=10,
                 verification_key=None):
        self.user_id = user_id
        self.user_name = user_name
        self.number_of_tickets = number_of_tickets
        self.ports = ports

        if verification_key == None:
            # TODO generate secret
            self.verification_key = "SECRET"
        else:
            self.verification_key = verification_key

    # get dict for saving as json serverside
    def get_dict(self):
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "number_of_tickets": self.number_of_tickets,
                "verification_key": self.verification_key,
                "ports": self.ports}

    def get_client_setup_dict(self):
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "number_of_tickets": self.number_of_tickets,
                "verification_key": self.verification_key,
                "ports": self.ports}

    def generate_client_setup_file(self):
        setup_file = "client_setup_{}_{}.json".format(self.user_id, self.user_name)
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
                                                  number_of_tickets=user["number_of_tickets"],
                                                  verification_key=user["verification_key"],
                                                  ports=user["ports"]))
            self.id_count = state_dict["id_count"]

    #  adds new user and saves new user to json
    def add_user(self, user_name, number_of_tickets, ports):
        new_user = ServerStateUser(user_id=self.id_count,
                                   user_name=user_name,
                                   number_of_tickets=number_of_tickets,
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