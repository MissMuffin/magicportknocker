from util.client_state import ClientState
import click
import socket
import sys
from util.packet import Packet
import requests
from util.auth import generate_nth_token, generate_secret
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
    time.sleep(0.25 * i * 3)
sock.close()

# trying establishing tcp connecktion to authorized port
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((state.server_ip, state.ports[-1]))


# try authentication with n-1 ticket


# try authentication with n-2 ticket

# show error

# if success
# save to file: decrement ntickets
# show success
