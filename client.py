import socket
import sys
import auth
import packet
from state import State
import state

state.file_name = "state.json"

try:
    state = State.load()
except FileNotFoundError:
    secret = input("Please input the secret: ").strip()
    number_of_tickets = int(input("Please input the number of tickets: "))
    state = State(secret, number_of_tickets)
    state.save()

ticket = auth.generate_nth_token(state.secret, state.number_of_remaining_tickets)
ip = "1"
server_address = ('localhost', 10000)
p = packet.Packet(ticket, ip)
buffer = p.pack(state.secret)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    # Send data
    print('sending {!r}'.format(buffer))
    # TODO resend with sleep?
    sock.sendto(buffer, server_address)

    # Receive response
    print('waiting for response')
    data, server = sock.recvfrom(4096)
    print('received {!r}'.format(data))

    state.number_of_remaining_tickets -= 1
    state.save()

finally:
    print('closing socket')
    sock.close()
