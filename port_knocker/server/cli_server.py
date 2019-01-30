import socket
import sys
from port_knocker.util.packet import Packet
from port_knocker.util.auth import verify_ticket
from port_knocker.util.server_state import ServerState

state = ServerState()
try:
    state.load()
except FileNotFoundError:
    print("Save file not found.")

def key_finder(user_id):
    # check if user exists
    user_state = state.get_user(user_id)

    if user_state == None:
        # TODO log auth attempt
        raise Exception("User does not exist")
    
    return user_state.symm_key

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
sock.bind(server_address)
print('listening on {} port {}'.format(*server_address))
print('\nlistening...')

while True:
    payload, address = sock.recvfrom(4096) # cant trust this address
    print('received {} bytes from {}'.format(len(payload), address))

    # try unpacking
    try:
        packet = Packet.unpack(payload, key_finder)
    except Exception as e:
        print(e)
        # TODO add logging
        continue

    # get user state
    user_state = state.get_user(packet.user_id)

    # check for correct ticket
    if verify_ticket(received_ticket=packet.ticket, server_ticket=user_state.secret):

        # update server state and save
        # user_state.secret = packet.ticket
        # user_state.number_of_remaining_tickets -= 1
        # state.save()

        # emulate open ports
        print("ticket was correct")
        print("client ip:", packet.ip)
        print("authorized ports: {}".format(str(user_state.ports)))

    else:
        print("authentication failed")
