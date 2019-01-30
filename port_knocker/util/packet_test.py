from .packet import *
import pytest
import cryptography.exceptions
from base64 import b64encode
import os

def test_good():
#     secret = b64encode(os.urandom(32))
#     ticket = b64encode(os.urandom(32))
#     ip = "2"

#     p = Packet(ticket, ip)
#     buffer = p.pack(secret)

#     unpacked = Packet.unpack(secret, buffer)
#     assert unpacked.ticket == ticket and unpacked.ip == ip
    pass

def test_bad_signature():
#     secret = b"secret"
#     ticket = b"t"
#     ip = "2"

#     p = Packet(ticket, ip)
#     buffer = p.pack(secret)


#     with pytest.raises(cryptography.exceptions.InvalidSignature):
#         Packet.unpack(b"differnt_secret", buffer)
        pass
