from port_knocker.util.client_state import ClientState
import click
import socket
import sys
from port_knocker.util.packet import Packet
import requests
from port_knocker.util.auth import generate_nth_token, generate_secret
import time
import os

# check if save file exists
# no: read setup, save to file
save_file = "save_file.json"
state = None # type: ClientState
try:
    state = ClientState.load(save_file)
except:
    click.echo("Save file not found.")

def try_tcp(server_ip, port, timeout=1.0):
    # trying establishing tcp connecktion to authorized port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((server_ip, port))
        return True
    except:
        return False
    finally:
        sock.close()
    


# create packet to send
ip = requests.get('https://ip.blacknode.se').text
ticket = generate_nth_token(state.secret, state.n_tickets)
new_ticket = b""
if state.n_tickets == 1:
    new_ticket = generate_secret()
p = Packet(ip, state.user_id, ticket, new_ticket)
payload = p.pack(state.symm_key)

# create udp socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for i in range(10):    
    sock.sendto(payload, ("localhost", 10000))
    timeout = 0.25 * i * 3
    if try_tcp(state.server_ip, int(state.ports[0])):
        print('Success! Ports are now open!')
        break
    else:
        print("retrying in {timeout} seconds...".format(timeout=timeout))
        time.sleep(timeout)
sock.close()



# try authentication with n-1 ticket


# try authentication with n-2 ticket

# show error

# if success
# save to file: decrement ntickets
# show success
