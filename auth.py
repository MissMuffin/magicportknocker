from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

def hash(hash_input): 
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(hash_input)
    return digest.finalize()

def verify(a, b):
    return hash(a) == b

def generate_tokens(seed, number_of_tokens):
    tickets = list()
    # init first entry
    tickets.append(hash(seed.encode()))

    for i in range(number_of_tokens - 1):
        tickets.append(hash(tickets[-1]))

    return tickets

def generate_nth_token(seed, n):
    ticket = hash(seed.encode())
    for i in range(n - 1):
        ticket = hash(ticket)

    return ticket