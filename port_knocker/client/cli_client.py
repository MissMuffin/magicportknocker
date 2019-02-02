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

# check if save file exists
# note: save file and setup file have identical structure
save_file = "save_file.json"
state = None # type: ClientState
try:
    state = ClientState.load(save_file)
except:
    click.echo("Save file not found.")

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

# query server for public ip address
public_ip = requests.get('https://ip.blacknode.se').text

# generator for remaining tickets
remaining_tickets = state.remaining_tickets()

new_secret = b""
new_n = 0
new_ticket = b""

# if all but 2 tickets have been used: generate new ticket secret
# 2 because: if server desync happened we need one backup ticket
if state.n_tickets == 2:
    new_secret = generate_secret()
    new_n = 100
    new_ticket = generate_nth_ticket(new_secret, new_n + 1)

def create_payload():
    # generate ticket
    ticket = generate_nth_ticket(state.secret, next(remaining_tickets))
    # create packet to send
    p = Packet(public_ip, state.user_id, ticket, new_ticket, new_n)
    return p.pack(state.symm_key)

''' 
try sending udp packet multiple times in case of packet loss
increase waiting time between resends in case packet takes a bit longer
to arrive
'''
# create udp socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# create payload
payload = create_payload()

# try authentication with n-1 ticket
for i in range(10):    
    sock.sendto(payload, ("localhost", 10000))
    timeout = 0.25 * i * 3
    if try_tcp(state.server_ip, int(state.ports[0])):
        print('Success! Ports are now open!')
        state.update_state(1, new_secret, new_n)
        break
    else:
        print("retrying in {timeout} seconds...".format(timeout=timeout))
        time.sleep(timeout)
sock.close()

# try authentication with n-2 ticket in case of server desync
# -> user authenticated successfully and server saved new ticket
# but before ports could be opened the server crashed

