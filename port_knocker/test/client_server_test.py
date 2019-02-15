from port_knocker.client.cli_client import Client
from port_knocker.server.cli_server import Server
from port_knocker.util.auth import *
from gevent.server import DatagramServer
from port_knocker.util.server_state import *
import uuid
from port_knocker.util.client_state import *
import types


def test(mocker):
    server_fname = str(uuid.uuid4()) + ".json"
    client_fname = str(uuid.uuid4()) + ".json"

    server_state = ServerState(save_file=server_fname, server_ip="127.0.0.1", auth_port="13337")
    server_state.add_user("tom", 8, [80], fname=client_fname)
    orig_cstate = server_state.get_user(0) # type:ClientState
    cstate = ClientState.load(client_fname)

    ip_addr = "95.90.236.125"

    def handle(socket, address):
        print("yay")

    server = DatagramServer(
        (cstate.server_ip, cstate.auth_port),
        handle)
    server.start()

    client = Client()
    mock_is_auth = mocker.patch.object(Client, "is_authenticated")

    # emulate successful auth on first attempt
    mock_is_auth.side_effect = [True]
    client.authenticate(state=cstate, ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
    assert cstate.n_tickets == orig_cstate.n_tickets - 1 
    # remaining tickets 7

    # emulate successful auth on second attempt
    mock_is_auth.side_effect = [False, True]
    client.authenticate(state=cstate, ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
    assert cstate.n_tickets == orig_cstate.n_tickets - 3
    # remainging tickets 5 

    # emulate successful auth on third attempt
    mock_is_auth.side_effect = [False, False, True]
    client.authenticate(state=cstate, ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
    assert cstate.n_tickets == orig_cstate.n_tickets - 6
    # remainging tickets 2

    # emulate no successful auth
    mock_is_auth.side_effect = [False, False, False]
    client.authenticate(state=cstate, ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
    assert cstate.n_tickets == orig_cstate.n_tickets - 6
    # remainging tickets 2 -> didnt change

    # state with 2 tickets remaining
    # n_tickets = 

    # # emulate new secret exchange
    # mock_is_auth.side_effect = [True]
    # new_secret, new_n = client.authenticate(state=cstate, ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
    # assert cstate.n_tickets == new_n
    # assert cstate.secret == new_secret

    # cstate = orig_cstate

    # # emulate new secret exchange with one desync
    # mock_is_auth.side_effect = [False, True]
    # new_secret, new_n = client.authenticate(state=cstate, ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
    # assert cstate.n_tickets == new_n
    # assert cstate.secret == new_secret

    # # emulate new secret exchange
    # mock_is_auth.side_effect = [False, False, True]
    # client.authenticate(state=cstate, ip_addr=ip_addr, tickets_to_try=3, resend_packet=0)
    # assert cstate.n_tickets == orig_cstate.n_tickets - 6
    # # remainging tickets 2 -> didnt change
 
    server.stop()

    
    