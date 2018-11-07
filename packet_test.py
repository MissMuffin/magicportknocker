from packet import *
import pytest
import cryptography.exceptions

def test_good():
    secret = "sdfsdhgh"
    ticket = "t"
    ip = "2"

    p = Packet(ticket, ip)
    buffer = p.pack(secret)

    unpacked = Packet.unpack(secret, buffer)
    assert unpacked.ticket == ticket and unpacked.ip == ip  

def test_bad_signature():
    secret = "secret"
    ticket = "t"
    ip = "2"

    p = Packet(ticket, ip)
    buffer = p.pack(secret)


    with pytest.raises(cryptography.exceptions.InvalidSignature):
        Packet.unpack("differnt_secret", buffer)
