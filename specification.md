# Specification

## In-depth description



## Requirements
- the project and its dependencies must be open source
- in the case that the server is compromised the attacker should not be able to find enough information to succesfully authenticate as a user  
- protection from replay attacks
- by default only the upd port used for authentication will receive packets, all other incomming traffic is to be dropped

## Functions

### Admin
- CRUD user
  - user id
  - user name
  - port privileges
  - number of tickets
  - generate secret
  - generate symmetric key
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