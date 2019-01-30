import struct
from collections import defaultdict

import netstruct
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from util.auth import generate_nth_token
from util.client_state import ClientState
from util.server_state import ServerStateUser


class Packet(object):

    ip = "" # type: String
    state = None # type: ClientState
    new_ticket = None

    def __init__(self, state, ip, new_ticket=None):
        self.ip = ip
        self.state = state
        if new_ticket != None:
            self.new_ticket = new_ticket

    def _encrypt(self):
        encoded_ip = self.ip.encode()
        ticket = generate_nth_token(self.state.secret, self.state.n_tickets)
        buffer = netstruct.pack(b'!b$b$b$', ticket, self.new_ticket, encoded_ip)

        aesgcm = AESGCM(self.state.symm_key)
        nonce = generate_nth_token(self.state.secret, self.state.n_tickets + 1)
        return aesgcm.encrypt(nonce, buffer, b"")

    def pack(self):
        ct = self._encrypt()
        return netstruct.pack(b'!b$b$', ct, self.state.user_id)
    
    @staticmethod
    def decrypt(user_state, ct):
        nonce = user_state.secret
        aesgcm = AESGCM(user_state.symm_key)
        buffer = aesgcm.decrypt(nonce, ct, b"")
        ticket, new_ticket, ip = netstruct.unpack(b'!b$b$b$', buffer)
        return ticket, ip.decode(), new_ticket

    @staticmethod
    def unpack(payload):
        ct, user_id = netstruct.unpack(b'!b$b$', payload)
        return ct, user_id
