import struct
from collections import defaultdict

import netstruct
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac


class Packet(object):

    ticket = ""
    ip = ""

    def __init__(self, ticket, ip):
        self.ticket = ticket
        self.ip = ip

    def pack(self, secret):
        # encoding defaults to utf8
        encoded_ticket = self.ticket.encode()
        encoded_ip = self.ip.encode()
        encoded_secret = secret.encode()

        # hmac signature from concat of encoded ticket and encoded ip 
        signature = Packet._sign(encoded_secret, encoded_ticket, encoded_ip)

        # pack
        return netstruct.pack(b'!b$b$b$', encoded_ticket, encoded_ip, signature)

    @staticmethod
    def unpack(secret, buffer):
        ticket, ip, signature = netstruct.unpack(b'!b$b$b$', buffer)
        Packet._verify_signature(secret.encode(), ticket, ip, signature)
        return Packet(ticket.decode(), ip.decode())

    @staticmethod
    def _verify_signature(secret, encoded_ticket, encoded_ip, signature):
        h = hmac.HMAC(secret, hashes.SHA256(), backend=default_backend())
        h.update(encoded_ticket + encoded_ip)
        return h.verify(signature)

    @staticmethod
    def _sign(secret, encoded_ticket, encoded_ip):
        h = hmac.HMAC(secret, hashes.SHA256(), backend=default_backend())
        to_sign = encoded_ticket + encoded_ip
        h.update(to_sign)
        return h.finalize()