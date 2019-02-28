import json
from base64 import b64encode, b64decode
import appdirs
from pathlib2 import Path
import click

class ClientState():

    appname = "MagicPortKnocker"
    appauthor = "Bianca Ploch"

    _savedir = appdirs.user_data_dir(appname, appauthor)
    _savefile = _savedir + "/savefile.json"
    _setup_file = "setup_file.json"
    
    user_id = 0
    user_name = ""
    n_tickets = 0
    secret = b"SECRET"
    symm_key = b"SYMM_KEY"
    ports = []
    server_ip = None
    auth_port = None

    def __init__(self, user_id, user_name, ports, n_tickets,
                 secret, symm_key, server_ip, auth_port):
        self.user_id = user_id
        self.user_name = user_name
        self.n_tickets = n_tickets
        self.ports = ports
        self.secret = secret
        self.symm_key = symm_key
        self.server_ip = server_ip
        self.auth_port = int(auth_port)

    def get_dict(self):
        # same structure as setup file for simplicity
        user_info = {"user_id": self.user_id,
                "user_name": self.user_name,
                "n_tickets": self.n_tickets,
                "secret": b64encode(self.secret).decode(),
                "symm_key":b64encode(self.symm_key).decode(),
                "ports": self.ports}
        return {"user": user_info,
                "server_ip": self.server_ip,
                "auth_port": self.auth_port}

    @staticmethod
    def _load(savefile):
        with open(savefile, "r") as f:
            client_info = json.load(f)
            user_info = client_info["user"]
            state = ClientState( user_id=user_info["user_id"],
                                user_name=user_info["user_name"],
                                n_tickets=user_info["n_tickets"],
                                secret=b64decode(user_info["secret"]),
                                symm_key=b64decode(user_info["symm_key"]),
                                ports=user_info["ports"],
                                server_ip=client_info["server_ip"],
                                auth_port=client_info["auth_port"])
            return state

    @staticmethod
    def load():
        try:
            # check for savefile
            return ClientState._load(ClientState._savefile)
        except:
            click.echo("Savefile not found. Looking for setup file...")
        
        try:
            # check for setup file
            state = ClientState._load(ClientState._setup_file)
            click.echo("Setup file found. Creating savefile...")
        except:
            raise FileNotFoundError("Setup file not found. Contact your admin.")
        
        try:
            # create savefile from setup file
            state.save()
            click.echo("Savefile successfully created.")
        except Exception as e:
            raise Exception("Could not create savefile. {}".format(e))

        return state

    def save(self):
        Path(self._savedir).mkdir(exist_ok=True, parents=True)
        setup = self.get_dict()
        with open(self._savefile, "w+") as f:
            json.dump(setup, f, indent=4)

    def update_state(self, n_ticket_sent, new_secret, new_n):
        if new_n > 0:
            self.n_tickets = new_n
            self.secret = new_secret
        else:
            self.n_tickets -= n_ticket_sent
        self.save()
 