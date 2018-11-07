import socket
import sys
import packet
import auth
from state import State
import state

state.file_name = "server_state.json"

try:
    state = State.load()
except FileNotFoundError:
    secret = input("Please input the secret: ").strip()
    number_of_tickets = int(input("Please input the number of tickets: "))
    state = State(secret, number_of_tickets)
    state.save()

ticket = auth.generate_nth_token(state.secret, state.number_of_remaining_tickets + 1)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('listening on {} port {}'.format(*server_address))
sock.bind(server_address)

while True:
    print('\nlistening...')
    buffer, address = sock.recvfrom(4096) # cant trust this address

    # unpack and verify signature
    unpacked_buffer = packet.Packet.unpack(state.secret, buffer)
    client_ticket = unpacked_buffer.ticket
    client_ip = unpacked_buffer.ip

    # check for correct ticket
    if auth.verify_ticket(client_ticket, ticket):

        ticket = client_ticket

        print('received {} bytes from {}'.format(len(buffer), address))
        print("ticket was correct")
        print("client ip:", client_ip)

        state.number_of_remaining_tickets -= 1
        state.save()

        sent = sock.sendto("opened port".encode(), address)
        print('sent {} bytes back to {}'.format(sent, address))
    
    else:
        print("authentication failed")
