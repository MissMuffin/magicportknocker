# Specification

This project allows users temporary port access on a server using a [hash chain token](https://en.wikipedia.org/wiki/Hash_chain).

Token and ticket are used interchangeably.

## Project structure

The project consists of three small programs:
The server which handles incoming requests to open ports on the host
The client used by the user(s) wanting to authorize use of certain ports
The admin CLI which allows a system administrator to manage users.

## In-depth description

A user is privileged to access certain ports of a server. In order to be able to connect to the server’s ports the user has to authenticate themselves. 

This is done on the basis of a shared secret, which is known to both user and server before any authentication attempt is started.

## Requirements and requirements fulfillment
1. The project and its dependencies must be open source

    ```
    Yes.
    ```

2.  In the case that the data on the server is compromised (we assume read-only access) the attacker should not be able to find enough information to successfully authenticate as a user  

    ```
    This is addressed by using a hash chain token for authentication. The user uses the nth token in the chain while the server has the (n+1)th token saved on disk. The token received from the user is then hashed once more and compared to the saved token. We take advantage of the one-way property of the hash chain: the hash function has no inverse and a token from the chain cannot be used to compute an earlier token of that chain. By reading the (n + 1)th token saved on the server the attacker cannot gleam any information on what the nth token might be.
    ```

3. Protection from replay attacks

    ```
    After a token has been used it expires. Replaying an authentication packet sent to the server will not authenticate again.
    
    Not covered is the situation where the attacker captures and drops all authentication packets from the client. Assuming the attacker is able to connect to the same network as the client at the time when the authentication packet was created, the attacker is then able to replay the captured packets and successfully authenticate.
    ```

4. Using nmap server to scan the server will reveal no open ports 

    ```
    By default only the UDP port used for authentication will receive packets, all other incoming traffic is to be dropped.
    ```

## Authentication protocol

![alt text](https://github.com/MissMuffin/magicportknocker/blob/master/images/flow_chart_client.png "Client flow chart")

![alt text](https://github.com/MissMuffin/magicportknocker/blob/master/images/flow_chart_server.png "Server flow chart")

A ticket is derived from the ticket secret $x$ by computing the hash function $h(x)$. To compute a ticket the ticket secret is hashed n times, where n is the number of tickets allotted to the user. The default value for n is 100:

```
First ticket = h^100(x)     where x is the ticket secret.
```

On the server the result of computing $h^{101}(x)$ is stored. Upon receiving a ticket from the client the received ticket is hashed again and compared to the stored ticket. 

```
Stored ticket = h^101(x)
Received ticket = h^100(x)

Evaluate: Stored ticket == h(received ticket)
if      True:   authentication succeeds
        False:  auenthication fails
```

Are both identical then the ticket holder is assumed to be the authorized user and the authentication is successful --- otherwise the authentication fails.

The ticket secret and the derived tickets are 32 bytes long. To derive the nth ticket the secret is hashed n times using SHA256. For the first authentication the nth ticket is used. By using a hash function to derive tickets, even if a ticket is captured by an attacker it cannot be used to derive any following tickets.

*TL;DR:*

1. Compute ticket
2. Put together packet for authentication and send to server
3. Check for successful authentication by trying to connect to ports

### Server-side authentication

#### Successful

In the case of a successful authentication the received ticket is saved and the old ticket is thrown away. The server's iptables are adjusted to allow the client to establish TCP and UDP connections to their privileged ports. The situation when the ports are opened for the user’s IP address will hereafter be called a session. 

Since there is no outgoing communication from the server, the only way the client will know whether an authentication attempt succeeded is by attempting to connect to each of their privileged ports via TCP. Are all connection attempts successful then authentication was successful (for this something needs to be listening on the ports in question, for example a simple web server serving a webpage).

#### Unsuccessful

Any packets that the server cannot unpack are classified as invalid, logged, and disregarded. Packets that can be unpacked and decrypted successfully, but whose contained data then fails to correspond to a valid user or do not contain the correct ticket are also logged and then disregarded.

### Client-side authentication

#### Unsuccessful

Should any or even all of the attempt to connect to the user’s privileged ports fail then the authentication will be seen as unsuccessful. In this case the authentication process is repeated with the next ticket. This mechanism exists to counteract possible desynchronisation between the client state and the server state. A desynchronisation might occur when, after the client successfully authenticated, the server saves the new ticket to disk but fails to open the user's privileged ports, e.g. due to a server crash since sessions do not persist after a server reboot.

Encountering further failure to authenticate leads to attempting to authenticate using the next ticket. This will continue until maximum number of tickets to try for authentication have been used. In the case that the client is still not authenticated after trying the maximum number of tickets an error message will be displayed to indicate to the user that there has been a problem authenticating and that the user's administrator should be contacted. An unsuccessful authentication might mean any of the following:
- the client's and server's data does not match (symmetric key, ticket, privileged ports)
- the server is down.
Any of these issues need to be addressed by the server administrator.

#### Successful

When any one of the tickets tried authenticates successfully, i.e. a TCP connection to all privileged ports can be established, then the client will decrement the number of tickets left by however many tickets have been used for the successful authentication.

### Using up all allocated tickets and generating a new ticket secret

Should the number of remaining tickets at any time during an authentication become equal or less than two then a new ticket secret will be generated. From this new secret the first new ticket is derived and together with the new number of tickets sent to the server. A number of tickets greater than zero indicates for the server that the client has generated a new secret and the first new ticket of the new secret will need to be saved to disk instead of the received ticket based on the old secret.

## Implementation

### Setup file generation

To begin the user is added to the list of authorized users by using the admin-program. While adding the user they are also assigned port privileges for the server and a certain number of tickets. The admin-program then generates a server configuration file and a client setup file. These files contain the following:

```
Client setup file
- the server ip
- the authentication port for the server
- the number of tickets
- the ticket secret used to derive all tickets from
- the symmetric key used for encrypting the ticket sent to the server
- the user id
- the list of privileged ports
```
```
Server configuration file
- the id counter
- the public server ip
- the authentication port
- a list of users each containing
  - user id
  - user name
  - current ticket
  - symmetric key
  - list of privileged ports
```

The client setup file needs to be forwarded to the user and placed in the program's root directory. It is then used to initialize the client configuration. Note that after generating the setup file the ticket secret is not saved in the server configuration file, only the first ticket, derived from the ticket secret, is saved on the server.

### Ticket encryption, packaging, sending

The packet contains the following fields:
- user ip
- ticket
- new number of tickets
- new ticket
- user id (unencrypted).

The packet is packed into binary data suitable to be sent over the network using the [netstruct](https://pypi.org/project/netstruct/) library. The data is then encrypted using AES GCM (Galois Counter Mode) from the [cryptography](https://cryptography.io/en/latest/hazmat/primitives/aead/) library. AES GCM is an authenticated encryption which provides both data authenticity and confidentiality. For the encryption the user's symmetric key and a random 32 byte salt/nonce is used.

The new number of tickets is used as a flag: if the received value is greater than zero, the client has generated a new ticket secret and sent the first ticket along.

The encrypted packet together with the user id  and a nonce is then packed using netstruct and sent to the server's authentication port using UDP.

### Port opening and closing with iptables

All ports on the server with the exception of the authentication port and the SSH port are closed and drop all incoming traffic. The SSH port does not necessarily be kept open, instead when running the Magic Portknocker server program on the server anyone wanting to connect over SSH could do so using the client program, given that they have a valid client setup. 

Every change made to iptables is reset daily --- this means that all authenticated user's privileged ports are closed at the same time every day without regard as to when the user authenticated. If the daily reset happens at 22:00 and a user authenticated 21:55 then every user's privileged ports are closed and the user has to authenticate again in order to be able to connect.

When updating or removing a user the administrator is given the option to close all currently open user ports. Individual closing of a user's ports is not possible since the correlation of IP addresses and users is not saved upon user authentication. Upon removing all users ports are automatically closed as well. Furthermore, the administrator can manually reset iptables by calling the script used for the CRON job located in ```scripts/iptables-reset```.

## Concerns
- Ticket hashing might require salt to be stronger (one collision in the chain makes all following hashes vulnerable otherwise)
- When client checks if TCP connection possible: if one port is not open authentication is seen as failure and client will become desynced from server
- No way to close individual connection by admin
- No way for client to close connection after authenticating
- Multiple users might have the same ip e.g. if they share the same network

## Possible future features
- Client can start and close their session by calling the client program with the parameters start and stop
- Save every authenticated user's ip to allow individual closing of their corresponding privileged ports
  - Would also allow admin to view all currently authenticated users
- Make authenticated sessions persistent
- Allow for a time limit to be set for an individual authenticated session