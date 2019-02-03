# Readme

## Setup

pip install -e .

pip3 install -U --user "git+https://github.com/MissMuffin/magicportknocker#egg=port-knocker"

## 

## Run Admin
python -m port_knocker.server.cli_admin

## Run Server
python -m port_knocker.server.cli_server

## Run Client
python -m port_knocker.client.cli_client

## run nginx to allow tcp connection for client to mock auth testing
sudo docker run -p 80:80 nginx
