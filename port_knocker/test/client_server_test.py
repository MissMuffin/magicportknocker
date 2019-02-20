from port_knocker.client.cli_client import Client
from port_knocker.server.cli_server import Server
from port_knocker.util.auth import *
from gevent.server import DatagramServer
from port_knocker.util.server_state import *
import uuid
import port_knocker.server.iptables
from port_knocker.util.client_state import *
import types
import multiprocessing
import pytest
import time


@pytest.fixture()
def background_server():
    class zzz:
        process = None    
        server = Server()
        open_ports_mock = None
        
        def start(self):            
            def _main():                
                self.server.run()

            self.process = multiprocessing.Process(target=_main)
            self.process.start()

    z = zzz()
    yield z

    if z.process:
        z.process.terminate()


def fresh_files(path):
    server_fname = str(path / (str(uuid.uuid4()) + ".json"))
    client_fname = str(path / (str(uuid.uuid4()) + ".json"))
    server_state = ServerState(save_file=server_fname, server_ip="127.0.0.1", auth_port="13337")
    server_state.add_user("tom", 8, [80], fname=client_fname)
    return server_fname, client_fname
    
def assert_tickets_synced(background_server, client):
    sstate = background_server.server.load_savefile()
    cstate = client.load_save_file()

    new_client_ticket = generate_nth_ticket(cstate.secret, cstate.n_tickets)
    new_server_ticket = sstate.get_user(0).ticket

    synced = verify_ticket(new_client_ticket, new_server_ticket)
    assert synced

    return cstate.secret, new_client_ticket, new_server_ticket

def test_end_to_end(mocker, background_server, tmp_path):

    server_cfg, client_cfg = fresh_files(tmp_path)
    
    client = Client()
    client.save_file = client_cfg
    # emulate checking for open ports after a successful authentication
    ## alternate False, True: first check is if ports are already open to
    ## avoid authenticating twice
    mock_is_auth = mocker.patch.object(Client, "is_authenticated")
    mock_is_auth.side_effect = [False, True] * 30

    background_server.server.save_file = server_cfg
    # overwrite open ports script to do nothing for this test
    mocker.patch.object(background_server.server, 'open_ports')

    # check that inital setup is synced
    first_secret, current_client_ticket, current_server_ticket = assert_tickets_synced(background_server, client)

    background_server.start()
    time.sleep(0.5) # give server process time to start
    
    client.run()
    time.sleep(0.5) # give server process time to write to disk

    # check that tickets are synced after one successful authentication
    _, new_client_ticket, new_server_ticket = assert_tickets_synced(background_server, client)

    # assert ticket have changed after one successful authentication
    assert new_server_ticket != current_server_ticket
    assert new_client_ticket != current_client_ticket

    for i in range(12):
        client.run()
        time.sleep(0.5)

    # assert that authentication continues when all tickets have been used up
    new_secret, _, _ = assert_tickets_synced(background_server, client)

    # assert that a new secret has been generated
    assert first_secret != new_secret

# def test_end_to_end_with_desync(mocker, background_server, tmp_path):
#     """
#     Test that authentication still succeeds when there is a ticket desync of 2. This situation may occur
#     when the server received a correct authentication attempt from a client and saved the new ticket to disk,
#     but before the corresponding ports could be openend the server crashed. In this test, we assume this process
#     happend twice, therefore a desync of two tickets.
#     """

#     server_cfg, client_cfg = fresh_files(tmp_path)
    
#     client = Client()
#     client.save_file = client_cfg
#     # emulate checking for open ports after a successful authentication
#     ## alternate False, False, False, True: first check is if ports are already open to
#     ## avoid authenticating twice, after that check are for successful authentication
#     mock_is_auth = mocker.patch.object(Client, "is_authenticated")
#     mock_is_auth.side_effect = [False, False, False, True] * 5

#     background_server.server.save_file = server_cfg
#     # overwrite open ports script to do nothing for this test
#     mocker.patch.object(background_server.server, 'open_ports')

#     # check that inital setup is synced
#     first_secret, current_client_ticket, current_server_ticket = assert_tickets_synced(background_server, client)

#     background_server.start()
#     time.sleep(0.5) # give server process time to start
    
#     client.run()
#     time.sleep(0.5) # give server process time to write to disk

#     # check that tickets are synced after one successful authentication
#     _, new_client_ticket, new_server_ticket = assert_tickets_synced(background_server, client)

#     # assert ticket have changed after one successful authentication
#     assert new_server_ticket != current_server_ticket
#     assert new_client_ticket != current_client_ticket

#     for i in range(12):
#         client.run()
#         time.sleep(0.5)

#     # assert that authentication continues when all tickets have been used up
#     new_secret, _, _ = assert_tickets_synced(background_server, client)

#     # assert that a new secret has been generated
#     assert first_secret != new_secret

def test_end_to_end_failure(capsys, mocker, background_server, tmp_path):
    """
    Test for correct behavior when the authentication attempt fails. The cause for a failure 
    to authenticate Correct behavior could be a ticket desync > 2 or when the server is down.
    Correct behavior is the printing of a user message to contact the admin.
    """

    server_cfg, client_cfg = fresh_files(tmp_path)
    
    client = Client()
    client.save_file = client_cfg
    client._resend_packet = 1

    mock_is_auth = mocker.patch.object(Client, "is_authenticated")
    mock_is_auth.side_effect = [False] * 30

    cstate = client.load_save_file()
    current_ticket = generate_nth_ticket(cstate.secret, cstate.n_tickets)
    client.run()

    captured = capsys.readouterr()
    assert "Trying" in captured.out

    # ticket should not have changed since authentication failed
    cstate = client.load_save_file()
    assert current_ticket == generate_nth_ticket(cstate.secret, cstate.n_tickets)

    background_server.server.save_file = server_cfg
    mocker.patch.object(background_server.server, 'open_ports')

    mock_is_auth.side_effect = [False, True] * 10

    _, current_client_ticket, current_server_ticket = assert_tickets_synced(background_server, client)

    background_server.start()
    time.sleep(0.5)

    client.run()
    time.sleep(0.5)

    _, new_client_ticket, new_server_ticket = assert_tickets_synced(background_server, client)

    assert new_server_ticket != current_server_ticket
    assert new_client_ticket != current_client_ticket   
    