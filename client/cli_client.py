from util.client_state import ClientState
import click
import socket
import sys
from util.packet import Packet
import requests

# check if save file exists
# no: read setup, save to file
save_file = ""
state = None # type: ClientState
try:
    state = ClientState.load(save_file)
except:
    click.echo("Save file not found.")

# create packet to send
ip = requests.get('http://ip.42.pl/raw').text
p = Packet(state, ip)
to_send = p.pack()

# create udp socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(to_send, ("localhost", 10000)) # TODO send multiple in case packet gets lost
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
