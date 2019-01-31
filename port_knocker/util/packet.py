import struct
from collections import defaultdict

import netstruct
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .auth import generate_nth_token
import os

class Packet(object):

    ip = ""
    user_id = None
    ticket = b""
    new_ticket = b""

    def __init__(self, ip, user_id, ticket, new_ticket=None):
        self.ip = ip
        self.user_id = user_id
        self.ticket = ticket
        if new_ticket != None:
            self.new_ticket = new_ticket

    def _encrypt(self, symm_key):
        buffer = netstruct.pack(b'!b$b$b$', self.ticket, self.new_ticket, self.ip.encode())
        aesgcm = AESGCM(symm_key)
        nonce = os.urandom(32)
        return aesgcm.encrypt(nonce, buffer, self.user_id), nonce

    def pack(self, symm_key):
        ct, nonce = self._encrypt(symm_key)
        return netstruct.pack(b'!b$b$b$', ct, nonce, self.user_id)
    
    @staticmethod
    def _decrypt(ct, nonce, symm_key):
        aesgcm = AESGCM(symm_key)
        buffer = aesgcm.decrypt(nonce, ct, b"")
        ticket, new_ticket, ip = netstruct.unpack(b'!b$b$b$', buffer)
        return ticket, ip.decode(), new_ticket

    @staticmethod
    def unpack(payload, key_finder):
        ct, nonce, user_id = netstruct.unpack(b'!b$b$b$', payload)
        symm_key = key_finder(user_id)
        ticket, ip, new_ticket = Packet._decrypt(ct, nonce, symm_key)
        return Packet(ip, user_id, ticket, new_ticket)