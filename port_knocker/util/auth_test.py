from .auth import *

def generate_tokens(secret, number_of_tokens):
    tickets = list()
    # init first entry
    tickets.append(hash(secret))

    for _ in range(number_of_tokens - 1):
        tickets.append(hash(tickets[-1]))

    return tickets

def test_generate_nth_token():
    n = 14
    seed = generate_secret()
    tokens = generate_tokens(seed, n)
    token_14th = generate_nth_token(seed, n)
    assert token_14th == tokens[-1]

def test_verify():
    n = 12
    seed = generate_secret()
    token_client = generate_tokens(seed, n)[-2]
    token_server = generate_nth_token(seed, n)
    assert verify_ticket(token_client, token_server)

def test_verify_bad():
    n = 12
    seed = generate_secret()
    token_client = generate_tokens(seed, n)[-1]
    token_server = generate_nth_token(seed, n)
    assert not verify_ticket(token_client, token_server)