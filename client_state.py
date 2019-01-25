import json


class ClientState():
    _save_file = None
    
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
        self.auth_port = auth_port

    def get_dict(self):
        # same structure as setup file for simplicity
        user_info = {"user_id": self.user_id,
                "user_name": self.user_name,
                "n_tickets": self.n_tickets,
                "secret": self.secret.decode(),
                "symm_key":self.symm_key.decode(),
                "ports": self.ports}
        return {"user": user_info,
                "server_ip": self.server_ip,
                "auth_port": self.auth_port}

    @staticmethod
    def load(save_file):
        with open(save_file, "r") as f:
            client_info = json.load(f)
            user_info = client_info["user"]
            state = ClientState( user_id=user_info["user_id"],
                                user_name=user_info["user_name"],
                                n_tickets=user_info["n_tickets"],
                                secret=user_info["secret"].encode(),
                                symm_key=user_info["symm_key"].encode(),
                                ports=user_info["ports"],
                                server_ip=client_info["server_ip"],
                                auth_port=client_info["auth_port"])
            return state

    def save(self, save_file="client_state.json"):
        setup = self.get_dict()
        with open(save_file, "w+") as f:
            json.dump(setup, f)
