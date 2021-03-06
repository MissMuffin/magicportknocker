import socket
import sys

import click
from elevate import elevate

from port_knocker.server.iptables import open_ports
from port_knocker.util.auth import verify_ticket
from port_knocker.util.packet import Packet
from port_knocker.util.security_logger import sec_logger
from port_knocker.util.server_state import ServerState


class Server():

    stop = False

    def load_savefile(self):
        state = ServerState()
        try:
            state.load()
            return state
        except FileNotFoundError:
            click.echo("Save file not found. Please do the initial setup via the admin cli.")
            sys.exit(1)

    def open_ports(self, ip, ports):
        open_ports(ip, ports)

    def run(self):

        state = self.load_savefile()

        def key_finder(user_id):
            '''
            Returns symmetric key for given use. Raises exception if user does not exist.
            '''
            user_state = state.get_user(user_id)
            if user_state == None:
                raise Exception("User {user_id} does not exist".format(user_id=user_id))
            return user_state.symm_key

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('0.0.0.0', state.auth_port)
        sock.bind(server_address)

        click.echo('listening on {} port {}'.format(*server_address))
        sec_logger.warn('listening on {} port {}'.format(*server_address))
        click.echo('listening...')
        sec_logger.info('listening...')

        while True:
            payload, address = sock.recvfrom(4096) # cant trust this address to be clients real address
            click.echo('received {} bytes from {}'.format(len(payload), address))

            try:
                packet = Packet.unpack(payload, key_finder)
            except Exception as e:
                if isinstance(e, FileNotFoundError):
                    click.echo(e)
                    sec_logger.warn('User attempting to authenticate does not exist.')
                else:
                    click.echo(e)
                    sec_logger.warn('Received weird packet, could not unpack.')
                continue

            # get user state
            user_state = state.get_user(packet.user_id)

            # check for correct ticket
            if verify_ticket(received_ticket=packet.ticket, server_ticket=user_state.ticket):
                sec_logger.info("{} ({}) was successfully authenticated".format(user_state.user_name, user_state.user_id))
                
                sec_logger.info("fname: {}".format(state._savefile))
                sec_logger.info("old: {}".format(user_state.ticket))

                # update server state and save
                if packet.new_n > 0:
                    user_state.ticket = packet.new_ticket
                else:
                    user_state.ticket = packet.ticket
                state.save()

                # open ports
                click.echo("ticket was correct")
                click.echo("client ip: {}".format(packet.ip))
                click.echo("authorized ports: {}\n".format(str(user_state.ports)))
                self.open_ports(packet.ip, user_state.ports)
            else:
                sec_logger.warn("authentication failed for {} ({})".format(user_state.user_name, user_state.user_id))

@click.command()
def main():
    '''
    Runs authentication server.
    '''
    # elevate this to root for modifying iptables
    elevate(graphical=False)
    Server().run()

if __name__ == "__main__":
    main()
