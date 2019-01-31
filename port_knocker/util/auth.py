from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import os

def hash(hash_input): 
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(hash_input)
    return digest.finalize()

def verify_ticket(received_ticket, server_ticket):
    return hash(received_ticket) == server_ticket

def generate_nth_token(ticket, n):
    for _ in range(n):
        ticket = hash(ticket)

    return ticket

def generate_secret():
    return os.urandom(32)