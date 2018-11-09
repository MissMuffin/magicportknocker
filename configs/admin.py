import os
import json
from base64 import b64encode

class User(json.JSONEncoder):
    user_id = 0
    user_name = ""
    n = 0
    signing_key = b""
    secret = b""
    privilege = ""
    verification_key = b""

    def __init__(self, user_id, user_name, n=10, signing_key=b"", verification_key=b"", secret=b"", privilege=""):
        self.user_id = user_id
        self.user_name = user_name
        self.n = n
        self.signing_key = signing_key
        self.verification_key = verification_key
        self.secret = secret
        self.privilege = privilege

    def get_server_config(self):
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "n": self.n,
                "privilege": self.privilege,
                "verification_key": self.verification_key.decode()}

    def get_user_setup(self):
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "n": self.n,
                "secret": self.secret.decode(),
                "signing_key": self.signing_key.decode()}

# define number of tickets
number_of_tickets = 10

# enter users and their privileges
users = []
user_id = 0

while True:
    name = input("Enter user name. Enter exit to stop\n")
    
    if name == 'n':
        break
    elif name == '':
        print("Name can't be empty")
        continue

    privilege = input("Enter user privilege. Default will be port 8080.\n")
    #  TODO check if integer and if valid port? for now only string for debugging
    if privilege == "":
        privilege = '8080'

    users.append(User(user_id=user_id, user_name=name, n=number_of_tickets, privilege=privilege))
    user_id += 1

# generate other stuff and write config to disk
server_config_output = []
for user in users:
    # string of random bytes
    user.secret = b64encode(os.urandom(10))

    # generate sign/verify key pair
    user.signing_key = b64encode(os.urandom(10))
    user.verification_key = b64encode(os.urandom(10))

    # save user setup files
    fname = "usersetup_" + str(user.user_id) + ".json"
    with open(fname, "w") as f:
        json.dump(user.get_user_setup(), f)

    server_config_output.append(user.get_server_config())

# save server config file
fname = "serverconfig.json"
with open(fname, "w") as f:
    json.dump(server_config_output, f)
