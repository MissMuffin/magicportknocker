import base64
import os
import socket
import sys
import time

import appdirs
import click
import requests

from port_knocker.config.config import Config
from port_knocker.util.auth import generate_nth_ticket, generate_secret, hash
from port_knocker.util.client_state import ClientState
from port_knocker.util.packet import Packet


class Client():

    _state = None # type: ClientState
    _resend_packet = Config.NUMBER_OF_PACKET_RESENDS

    def is_authenticated(self, server_ip, port, timeout=1.0):
        # try establishing tcp connection to a authorized port
        # to see if authentication was successful and port has been opened
        # or if authentication is not needed because port is already open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((server_ip, port))
            return True
        except:
            return False
        finally:
            sock.close()

    def get_ip(self, private=False):
        ip_addr = None
        if private:
            # read local ip from socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_addr = s.getsockname()[0]
            s.close()
        else:
            # query server to get public ip
            ip_addr = requests.get('https://ip.blacknode.se').text
        return ip_addr

    def create_payload(self, n, secret, n_tickets, ip_addr, user_id, symm_key, new_secret=None, new_n=0):
        
        ticket = generate_nth_ticket(secret, n_tickets - n)
       
        new_secret = new_secret
        new_n = new_n
        new_ticket = b""    

        # if all but 2 tickets have been used: generate new ticket secret
        # 2 because: if server desync happened we need one backup ticket
        if n_tickets <= 2 and not new_secret:
            new_secret = generate_secret()
            new_n = Config.DEFAULT_NUMBER_OF_TICKETS
            new_ticket = generate_nth_ticket(new_secret, new_n + 1)

        # create packet to send
        p = Packet(ip_addr, user_id, ticket, new_ticket, new_n)

        return p.pack(symm_key), new_secret, new_n

    def load_savefile(self):
        try:
            return ClientState.load()
        except Exception as e:
            click.echo(e)
            sys.exit(1)

    def authenticate(self, ip_addr=None, tickets_to_try=Config.TICKETS_TO_TRY, resend_packet=5):
        ''' 
        try sending udp packet multiple times (5) in case of packet loss
        increase waiting time between resends in case packet takes a bit longer
        to arrive
        '''
        # create udp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        new_secret = None
        new_n = 0

        # try authentication with n-1 ticket
        finished = False
        for n in range(tickets_to_try):
            payload, new_secret, new_n = self.create_payload(n, 
                                                            self._state.secret, 
                                                            self._state.n_tickets, 
                                                            ip_addr,
                                                            self._state.user_id, 
                                                            self._state.symm_key, 
                                                            new_n=new_n, 
                                                            new_secret=new_secret)
            for i in range(resend_packet + 1):
                sock.sendto(payload, (self._state.server_ip, self._state.auth_port))
                click.echo("sending ticket")
                timeout = 0.25 * i * 3
                if all(self.is_authenticated(self._state.server_ip, int(port)) for port in self._state.ports):
                    click.echo('Success! Ports are now open!')
                    self._state.update_state(n + 1, new_secret, new_n)
                    finished = True
                    break
                else:
                    click.echo("retrying in {timeout} seconds...".format(timeout=timeout))
                    time.sleep(timeout)

            if finished:
                break
            click.echo('Retrying with next ticket...')

        if not finished:
            click.echo('Could not authenticate with {} tickets. Contact admin'.format(tickets_to_try))

        sock.close()
        return new_secret, new_n

    def run(self, server_in_private_network=False):        
        # load client state        
        self._state = self.load_savefile()

        # get ip address
        ip_addr = self.get_ip(private=server_in_private_network)
        click.echo("Trying to authenticate at {}:{}. Server is in {} Network and own ip is {}".format(
                self._state.server_ip, self._state.auth_port, 
                "private" if server_in_private_network else "public",
                ip_addr))
                    
        # Skip the authencation altogether if ports are already open.
        if all(self.is_authenticated(self._state.server_ip, int(port)) for port in self._state.ports):
            click.echo('No authentication needed, privileged ports are already open!')
            return

        self.authenticate(ip_addr=ip_addr, resend_packet=self._resend_packet)        

@click.command()
@click.option("-p", "--private", default=False, show_default=True, is_flag=True)
def main(private):
    '''
    Tries to authenticate with server to facilitate opening of privileged ports.
    '''
    Client().run(private)

if __name__ == "__main__":
    main()
