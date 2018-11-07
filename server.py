import socket
import sys
import packet
import auth

secret = "dgkndklfjngkdlfjnk"
number_of_tickets = 100
ticket = auth.generate_nth_token(secret, number_of_tickets)

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
    unpacked_buffer = packet.Packet.unpack(secret, buffer)
    client_ticket = unpacked_buffer.ticket
    client_ip = unpacked_buffer.ip

    # check for correct ticket
    if auth.verify_ticket(client_ticket, ticket):

        ticket = client_ticket

        print('received {} bytes from {}'.format(len(buffer), address))
        print("ticket was correct")
        print("client ip:", client_ip)

        sent = sock.sendto("opened port".encode(), address)
        print('sent {} bytes back to {}'.format(sent, address))
    
    else:
        print("authentication failed")
