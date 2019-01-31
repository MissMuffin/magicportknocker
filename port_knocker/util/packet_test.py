from .packet import *
import pytest
import cryptography.exceptions
from base64 import b64encode
import os
from .auth import *

def test_good():
    user_id = 89
    ip = "2"
    ticket = generate_secret()
    new_ticket = generate_secret()
    new_n = 9
    symm_key = generate_secret()

    p = Packet(ip, user_id, ticket, new_ticket, new_n)
    payload = p.pack(symm_key)

    def fake_key_finder(_):
        return symm_key

    rec_p = Packet.unpack(payload, fake_key_finder)

    assert rec_p.user_id == user_id
    assert rec_p.ip == ip
    assert rec_p.ticket == ticket
    assert rec_p.new_ticket == new_ticket
    assert rec_p.new_n == new_n

