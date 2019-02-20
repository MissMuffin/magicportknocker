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
    time.sleep(0.5)
    
    client.run()
    time.sleep(0.5)

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

   

# def test(mocker, tmp_path):
#     server_fname = str(tmp_path / (str(uuid.uuid4()) + ".json"))
#     client_fname = str(tmp_path / (str(uuid.uuid4()) + ".json"))

#     server_state = ServerState(save_file=server_fname, server_ip="127.0.0.1", auth_port="13337")
#     server_state.add_user("tom", 8, [80], fname=client_fname)
#     orig_cstate = server_state.get_user(0) # type:ClientState
#     cstate = ClientState.load(client_fname)

#     ip_addr = "95.90.236.125"

#     def handle(socket, address):
#         print("yay")

#     server = DatagramServer(
#         (cstate.server_ip, cstate.auth_port),
#         handle)
#     server.start()

#     client = Client()
#     client.save_file = client_fname
#     client.load_save_file()
#     mock_is_auth = mocker.patch.object(Client, "is_authenticated")

#     # emulate successful auth on first attempt
#     mock_is_auth.side_effect = [True]
#     client.authenticate(ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
#     assert cstate.n_tickets == orig_cstate.n_tickets - 1 
#     # remaining tickets 7
# 
#     # emulate successful auth on second attempt
#     mock_is_auth.side_effect = [False, True]
#     client.authenticate(ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
#     assert cstate.n_tickets == orig_cstate.n_tickets - 3
#     # remainging tickets 5 

#     # emulate successful auth on third attempt
#     mock_is_auth.side_effect = [False, False, True]
#     client.authenticate(ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
#     assert cstate.n_tickets == orig_cstate.n_tickets - 6
#     # remainging tickets 2

#     # emulate no successful auth
#     mock_is_auth.side_effect = [False, False, False]
#     client.authenticate(ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
#     assert cstate.n_tickets == orig_cstate.n_tickets - 6
#     # remainging tickets 2 -> didnt change

#     # state with 2 tickets remaining
#     # n_tickets = 

#     # # emulate new secret exchange
#     # mock_is_auth.side_effect = [True]
#     # new_secret, new_n = client.authenticate(state=cstate, ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
#     # assert cstate.n_tickets == new_n
#     # assert cstate.secret == new_secret

#     # cstate = orig_cstate

#     # # emulate new secret exchange with one desync
#     # mock_is_auth.side_effect = [False, True]
#     # new_secret, new_n = client.authenticate(state=cstate, ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
#     # assert cstate.n_tickets == new_n
#     # assert cstate.secret == new_secret

#     # # emulate new secret exchange
#     # mock_is_auth.side_effect = [False, False, True]
#     # client.authenticate(state=cstate, ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
#     # assert cstate.n_tickets == orig_cstate.n_tickets - 6
#     # # remainging tickets 2 -> didnt change
 
#     server.stop()

    
    