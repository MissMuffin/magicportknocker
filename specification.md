Each file contains as follows# Specification

## In-depth description
A user is privileged to access certain ports of a server. In order to connect to these ports the user needs to authenticte themselves. This is done on the basis of a shared secret, which is known to both user and server before any authentication attempt is started. 

To begin the user is added to the list of authorized users by using the admin-program. while adding the user they are also assigned port privileges for the server and a certain number of tickets. The admin-program then generates a server configuration file and a client setup file. These files contain the following:

```
Client setup file
- the server ip
- the authentication port for the server
- the number of tickets
- the ticket secret
- the symmetric key
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

As the name suggests the client setup file needs to be forwarded to the user and placed in the program's root directory. It is then used to initalized the client configuration. Note that after generating the setup file the ticket secret is not saved in the server configuration file, only the first ticket, derived from the ticket secret, is saved on the server. A ticket is derived from the ticket secret by hashing the ticket secret a certain number of times. To get the first ticket the secret is therefore hashed n + 1 times, where n is the number of tickets allotted to the user. To autenticate the user hashes the ticket secret n times, where n is the number of tickets specified in the configuration file. On the server the received ticket is then hashed again and compared to the saved ticket. Are both identical then the ticket holder is assumed to be the authorized user and the authentication is successful --- otherwise the authentication fails and is written to the log.
In the case of a successful authentication the received ticket becomes the new saved ticket on the server and the servers iptables are adjusted to allow the client to establish tcp and udp connections to their privileged ports. Since there is no outgoing communication from the server, the only way the client will know wether an authentication attempt succeeded is by successfully establishing (and, of course, closing) a tcp connection with each of their privileged ports --- for this something needs to be listening on the concerned ports, for example a simple web server serving a webpage. Should this fail, 

because possible server client desync (server crash after saving new ticket, before opening ports)
server authentications not persistent after crash
up to 3 tickets
show error

If all connections are open the number of tickets will be reduced by however many tickets were used to succesfully authenticate.

how ticket is send
what packet contains
authenticated encryption
empty fields for new ticket (new n, new ticket)

daily iptables reset
admin can manually reset iptables
removing user gives option to reset iptables (see concerns: no individual connection closing)



## Concerns
- ticket hashing might require salt to be stronger (one collision in the chain makes all following hashes vulnerable otherwise)
- when client checks if tcp connection possible: if one port is not open authentication is seen as failure and client will become desynced from server
- no way to close individual connection by admin
- no way for client to close connection after authenticating

## Requirements
- the project and its dependencies must be open source
- in the case that the server is compromised the attacker should not be able to find enough information to succesfully authenticate as a user  
- protection from replay attacks
- by default only the upd port used for authentication will receive packets, all other incomming traffic is to be dropped

## Functions

### Admin
- create user
  - user id
  - user name
  - port privileges
  - number of tickets
  - generate secret
  - generate symmetric key
- update user (generates new setup file)
  - port privileges
  - generate new symmetric key
- remove user
- create setup file for clients
  - user id
  - user name
  - secret
  - symmetric key
  - privileged ports
  - number of tickets
  - authentication port
  - server ip
- create/update savefile for server state
  - id count
  - authentication port
  - public server ip
  - users
    - user id
    - user name
    - privileged ports
    - number of tickets
    - symmetric key
    - first ticket (secret hashed n times, where n is the number of tickets)

### Server
- update savefile for server state
- listens on authentication port for authentication protocol
- opens/closes ports

### Client
- use setup file from admin
- update savefile for client state (setup file == savefile)
  - same structure as setup file
- creates and sends authentication packet
  - contains user id, user ip, ticket
  - uses authenticated encryption