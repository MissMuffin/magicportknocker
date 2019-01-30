import socket
import sys
from util.packet import Packet
from util.auth import verify_ticket
from util.server_state import ServerState

state = ServerState()
try:
    state.load()
except FileNotFoundError:
    print("Save file not found.")

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
sock.bind(server_address)
print('listening on {} port {}'.format(*server_address))
print('\nlistening...')

while True:
    payload, address = sock.recvfrom(4096) # cant trust this address

    # unpack
    ct, user_id = Packet.unpack(payload)

    # check if user exists
    user_state = state.get_user(user_id)

    if user_state == None:
        # TODO log auth attempt
        print("user does not exist")
        continue

    # try decrypting
    ticket, ip, new_ticket = Packet.decrypt(user_state, ct)

    # check for correct ticket
    if verify_ticket(received_ticket=ticket, server_ticket=user_state.secret):

        # update server state and save
        user_state.secret = ticket
        user_state.number_of_remaining_tickets -= 1
        state.save()

        # emulate open ports
        print('received {} bytes from {}'.format(len(ct), address))
        print("ticket was correct")
        print("client ip:", ip)
        print("authorized ports: {}".format(str(user_state.ports)))

    else:
        print("authentication failed")
