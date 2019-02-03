from port_knocker.util.client_state import ClientState
import click
import socket
import sys
from port_knocker.util.packet import Packet
import requests
from port_knocker.util.auth import generate_nth_ticket, generate_secret, hash
import time
import os
import base64

def try_tcp(server_ip, port, timeout=1.0):
    # try establishing tcp connection to a authorized port
    # to see if authentication was successful
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((server_ip, port))
        return True
    except:
        return False
    finally:
        sock.close()


def main():
    # check if save file exists
    # note: save file and setup file have identical structure
    save_file = "save_file.json"
    state = None # type: ClientState
    try:
        state = ClientState.load(save_file)
    except:
        click.echo("Save file not found. Import save file from admin.")
        sys.exit(1)



    # query server for public ip address
    public_ip = requests.get('https://ip.blacknode.se').text
    public_ip = '192.168.0.5'

    # generator for remaining tickets
    # remaining_tickets = state.remaining_tickets()

    def create_payload(n):
        # generate ticket
        ticket = generate_nth_ticket(state.secret, state.n_tickets - n)
        import base64
        print(base64.b64encode(ticket))
        new_secret = b""
        new_n = 0
        new_ticket = b""    

        # if all but 2 tickets have been used: generate new ticket secret
        # 2 because: if server desync happened we need one backup ticket
        if state.n_tickets <= 2:
            new_secret = generate_secret()
            new_n = 100
            new_ticket = generate_nth_ticket(new_secret, new_n + 1)
        # create packet to send
        p = Packet(public_ip, state.user_id, ticket, new_ticket, new_n)
        return p.pack(state.symm_key), new_secret, new_n

    # Skip the authencation altogether if ports are already open.
    if all(try_tcp(state.server_ip, int(port)) for port in state.ports):
        print('No authentication needed, ports are already open!')
        sys.exit(0)

    ''' 
    try sending udp packet multiple times (5) in case of packet loss
    increase waiting time between resends in case packet takes a bit longer
    to arrive
    '''
    # create udp socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # try authentication with n-1 ticket
    finished = False
    tickets_to_try = 3
    for n in range(tickets_to_try):
        # create payload
        payload, new_secret, new_n = create_payload(n)
        for i in range(5):    
            sock.sendto(payload, (state.server_ip, state.auth_port))
            timeout = 0.25 * i * 3
            if try_tcp(state.server_ip, int(state.ports[0])):
                print('Success! Ports are now open!')
                state.update_state(n + 1, new_secret, new_n) # Something goes wrong here
                finished = True
                break
            else:
                print("retrying in {timeout} seconds...".format(timeout=timeout))
                time.sleep(timeout)

        if finished:
            break
        print('retrying with next ticket...')

    if not finished:
        print('Could not authenticate with {} tickets. Contact admin'.format(tickets_to_try))

    sock.close()

    # try authentication with n-2 ticket in case of server desync
    # -> user authenticated successfully and server saved new ticket
    # but before ports could be opened the server crashed


if __name__ == "__main__":
    main()