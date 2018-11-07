import socket
import sys
import auth
import packet

secret = "dgkndklfjngkdlfjnk"
#  one less than the server
number_of_tickets = 99
tickets = auth.generate_tokens(secret, number_of_tickets)

ip = "1"
server_address = ('localhost', 10000)
p = packet.Packet(tickets[-1], ip)
buffer = p.pack(secret)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    # Send data
    print('sending {!r}'.format(buffer))
    for i in range(3):
        sock.sendto(buffer, server_address)

    # Receive response
    print('waiting for response')
    data, server = sock.recvfrom(4096)
    print('received {!r}'.format(data))

finally:
    print('closing socket')
    sock.close()