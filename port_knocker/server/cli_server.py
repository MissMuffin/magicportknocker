import socket
import sys
from port_knocker.util.packet import Packet
from port_knocker.util.auth import verify_ticket
from port_knocker.util.server_state import ServerState
from port_knocker.util.security_logger import sec_logger
import logging

logging.basicConfig(level=logging.DEBUG)

state = ServerState()
try:
    state.load()
except FileNotFoundError:
    logging.error("Save file not found. Please do the initial setup via the admin cli.")
    sys.exit(1)

def key_finder(user_id):
    # check if user exists
    user_state = state.get_user(user_id)

    if user_state == None:
        # TODO log auth attempt
        raise Exception("User {user_id} does not exist".format(user_id=user_id))
    
    return user_state.symm_key

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
sock.bind(server_address)
logging.info('listening on {} port {}'.format(*server_address))
logging.info('listening...')

while True:
    payload, address = sock.recvfrom(4096) # cant trust this address
    logging.debug('received {} bytes from {}'.format(len(payload), address))

    # try unpacking
    try:
        packet = Packet.unpack(payload, key_finder)
    except Exception as e:
        logging.error(e)
        sec_logger.warn('Weird packet received.')
        continue

    # get user state
    user_state = state.get_user(packet.user_id)

    # check for correct ticket
    if verify_ticket(received_ticket=packet.ticket, server_ticket=user_state.secret):
        sec_logger.info("{} ({}) was successfully authenticated".format(user_state.user_name, user_state.user_id))

        # update server state and save
        if packet.new_n > 0:
            user_state.n_tickets = packet.new_n
            user_state.secret = packet.new_ticket   
        else:
            user_state.secret = packet.ticket
            user_state.n_tickets -= 1
        state.save()

        # emulate open ports
        logging.info("ticket was correct")
        logging.info("client ip: {}".format(packet.ip))
        logging.info("authorized ports: {}\n".format(str(user_state.ports)))

    else:
        sec_logger.warn("authentication failed for {} ({})".format(user_state.user_name, user_state.user_id))

