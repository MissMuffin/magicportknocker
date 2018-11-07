from auth import *

seed = "dsfsdf"

def test_generate_nth_token():
    n = 14
    tokens = generate_tokens(seed, n)
    token_14th = generate_nth_token(seed, n)
    assert token_14th == tokens[-1]

def test_verify():
    n = 12
    token_client = generate_tokens(seed, n)[-2]
    token_server = generate_nth_token(seed, n)
    assert verify(token_client, token_server)

def test_verify_bad():
    n = 12
    token_client = generate_tokens(seed, n)[-1]
    token_server = generate_nth_token(seed, n)
    assert not verify(token_client, token_server)