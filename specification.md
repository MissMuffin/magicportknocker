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

### Authentication protocol

As the name suggests the client setup file needs to be forwarded to the user and placed in the program's root directory. It is then used to initalized the client configuration. Note that after generating the setup file the ticket secret is not saved in the server configuration file, only the first ticket, derived from the ticket secret, is saved on the server. A ticket is derived from the ticket secret by hashing the ticket secret a certain number of times. To get the first ticket the secret is therefore hashed n + 1 times, where n is the number of tickets allotted to the user. To authenticate the user hashes the ticket secret n times, where n is the number of tickets specified in the configuration file. On the server the received ticket is then hashed again and compared to the saved ticket. Are both identical then the ticket holder is assumed to be the authorized user and the authentication is successful --- otherwise the authentication fails and is written to the log. 

#### Server-side authentication

##### Successful

In the case of a successful authentication the received ticket is saved and the old ticket is thrown away. The server's iptables are adjusted to allow the client to establish tcp and udp connections to their privileged ports. Since there is no outgoing communication from the server, the only way the client will know wether an authentication attempt succeeded is by successfully attempting a tcp connection with each of their privileged ports --- for this something needs to be listening on the ports in question, for example a simple web server serving a webpage. 

##### Unsuccessful

Any packets that the server cannot unpack are classified as 'weird', logged and disregarded. Packets that can be unpacked and decrypted successfully, but whose contained data then fails to correspond to a valid user or do not contain the correct ticket are also logged and then disregarded. Generally, packets are thrown away as early as possible when passing through the action chain of ```unpack -> check if user exists -> check for correct ticket``` in order to not block the servers ability to process authentication attempts for longer than necessary.

#### Client-side authentication

##### Unsuccessful

Should any or even all of the connection attempts fail then the authentication will be seen as unsuccessful. In this case the authentication process is repeated with the next ticket. This mechanism exists to counteract possible desynchronisation between the client state and the server state. A desynchronisation might occur when, after the client successfully authenticated, the server saves the new ticket to disk but fails to open the user's privileged ports, e.g. due to a server crash since authentications do not persist after a server reboot.

Encountering further failure to authenticate leads to attempting to authenticate using the next ticket. This will continue until maximum number of tickets to try for authentication have been used. This constant can be set in ```config.py```. In the case that the client is still not authenticated after trying the maximum number of tickets an error message will be displayed to indicate to the user that there has been a problem authenticating and that the user's administrator should be contacted. An unsuccessful authentication might mean any of the following: 
- the client's and server's data does not match (symmetric key, ticket, privileged ports)
- the server is down. 
Any of these issues need to be addressed by the server administrator.

##### Successful

When any one of the tickets tried authenticates successfully, i.e. a tcp connection to all privileged ports can be established, then the client will decrement the number of tickets left by however many tickets have been used for the successful authentication. 

#### Using up all allocated tickets and generating a new ticket secret

Should the number of remaining tickets at any time during an authentication become equal or less than two then a new ticket secret will be generated. From this new secret the first new ticket is derived and together with the new number of tickets sent to the server. A number of tickets greater than zero indicates for the server that the client has generated a new secret and the first new ticket of the new secret will need to be saved to disk instead of the received ticket based on the old secret.

#### How a ticket is encypted, packaged and sent

The 

how ticket is send
what packet contains
authenticated encryption
empty fields for new ticket (new n, new ticket)

### How iptables on the server

Every change made to iptables is reset daily --- this means that all authenticated user's privileged ports are closed at the same day every day without regard to the time the user authenticated. If the daily reset happens at 22:00 and a user authenticated 21:55 then this user's privileged ports are closed and the user has to authenticate again in order to be able to connect to his privileged ports. For this 
Furthermore the administrator can manually reset iptables by calling the script used for the CRON job located in ```scripts/iptables-reset```.

daily iptables reset
admin can manually reset iptables
removing user gives option to reset iptables (see concerns: no individual connection closing)



## Concerns
- ticket hashing might require salt to be stronger (one collision in the chain makes all following hashes vulnerable otherwise)
- when client checks if tcp connection possible: if one port is not open authentication is seen as failure and client will become desynced from server
- no way to close individual connection by admin
- no way for client to close connection after authenticating

## Possible future features
- client can start and close their session by calling the client program with the parameters start and stop
- save every authenticated user's ip to allow individual closing of their corresponding privileged ports
  - would also allow admin to view all currently authenticated users
- make authenticated sessions peristent
- allow for a time limit to be set for an individual authenticated session 

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