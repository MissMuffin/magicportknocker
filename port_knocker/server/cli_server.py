import socket
import sys

import click

from port_knocker.server.iptables import open_ports
from port_knocker.util.auth import verify_ticket
from port_knocker.util.packet import Packet
from port_knocker.util.security_logger import sec_logger
from port_knocker.util.server_state import ServerState


class Server():

    def run(self):

        state = ServerState()
        try:
            state.load()
        except FileNotFoundError:
            click.echo("Save file not found. Please do the initial setup via the admin cli.")
            sys.exit(1)

        def key_finder(user_id):
            user_state = state.get_user(user_id)
            if user_state == None:
                raise Exception("User {user_id} does not exist".format(user_id=user_id))
            
            return user_state.symm_key

        # create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # bind socket
        server_address = ('0.0.0.0', 13337)
        sock.bind(server_address)
        click.echo('listening on {} port {}'.format(*server_address))
        click.echo('listening...')

        while True:
            payload, address = sock.recvfrom(4096) # cant trust this address
            click.echo('received {} bytes from {}'.format(len(payload), address))

            # try unpacking
            try:
                packet = Packet.unpack(payload, key_finder)
            except Exception as e:
                if isinstance(e, FileNotFoundError):
                    click.echo(e)
                    sec_logger.warn('User attempting to authenticate does not exist.')
                else:
                    click.echo(e)
                    sec_logger.warn('Weird packet.')
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

                # open ports
                click.echo("ticket was correct")
                click.echo("client ip: {}".format(packet.ip))
                click.echo("authorized ports: {}\n".format(str(user_state.ports)))
                open_ports(packet.ip, user_state.ports)
            else:
                sec_logger.warn("authentication failed for {} ({})".format(user_state.user_name, user_state.user_id))

@click.command()
def main():
    '''
    Runs authentication server.
    '''
    Server().run()

if __name__ == "__main__":
    main()
