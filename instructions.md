# Step by step instructions

## You are exptected to have
- an Ubuntu computer to be the client
- an Ubuntu remote server that you connect to via ssh
- git and python3 installed on both

## To install 
1. ```
    git clone https://github.com/MissMuffin/magicportknocker.git
    ```
    or [download](https://github.com/MissMuffin/magicportknocker/archive/master.zip)
3.  ```
    cd magicportknocker/
    ``` 
4. make sure pip3 is installed 
    ```
    apt install python3-pip
    ```
5. make sure build-essential is installed 
    ```
    apt install build-essential
    ```
8. make sure python3-setuptools is installed
    ```
    apt install python3-setuptools
    ```
9.  install python package (exceute from inside repo)
    ```
    pip3 install .
    ```
    This will add portknock-[admin|client|server] to your PATH
10. make sure nginx is installed and running on necessary ports for presentation
    ```
    apt install nginx
    ```
11. If magicportknocker/scripts/iptables-reset is not exceutable for some reason make it executable with ```chmod +x```

## Setup iptables

[See here](https://github.com/MissMuffin/magicportknocker/blob/master/iptables.md)

## Configure CRON job for daily firewall reset
On the server run
```
crontab -u root -e
```
and copy/paste the following lines to schedule an iptables reset to the rules specified in you rules files at 22:00 daily.
```
    0 22 * * *      iptables-restore < /etc/iptables/rules.v4
    0 22 * * *      ip6tables-restore < /etc/iptables/rules.v6
```
This will automatically be added to the CRON jobs, but you can also manually restart the CRON service for more peace of mind ```service cron restart```.

To see which cron jobs are running for you
```
crontab -l
```
To see if cron job has run
```
tail -20 /var/log/syslog
```
To see if cron daemon is running
```
ps uww -C cron
```

## Run the server
1. 
    ```
    cd to magicportknocker dir
    ```
2. Setup server info and add first user
    ```
    portknock-admin add
    ```
3. Then copy /user_setup/username_id/setup_file.json to dir on client computer from where the client programm will be run
4. Start server
    ```
    nohup portknock-server > /dev/null 2>&1 & echo $! > server.pid
    ```
    This will save the pid of the server process to the file server.pic for easier stopping.
    ```
    kill pid
    ```

### Create service to automatically start the server on system start
1. Adjust `WorkingDirectory=/home/ubuntu/magicportknocker/` to where you put the repo
2. Copy file from systemd_file to /etc/systemd/system/
3. Make sure file has correct permissions (does not need to be executable)
    ```
    chmod 664 /etc/systemd/system/mpks.service
    ```
4. Reload systemd
   ```
   systemctl daemon-reload
   ```
5. Start the service
    ```
    systemctl start mpks.service
    ```
6. Configure automatic start on system boot
    ```
    systemctl enable mpks.service
    ```
7. Reboot and check if active with 
   ```
   systemctl is-active mpks.service
   ```


The server logs successful and failed authentication attempts to the file ```security.log``` in the repository directory.

## Authenticate using the client
Note: client authentication will only be succesful if something is listening on the user's privileged ports so that a tcp connection can be established. After an authentication attempt the client tries to tcp connect to all the user's privileged ports in order to determine wether the authentication was succesful. An easy solution for this is to serve a simple webpage on the ports in question using nginx.

1. Make sure you have the ```setup_file.json``` from the user_setup dir on the server in root dir from where you run the client
2. 
    ```
    portknock-client
    ```

## After changing things

After changing project: reinstall from magiportknocker dir
```
pip3 install --upgrade --force-reinstall .
```

Changed service file: reload daemon, restart service
```
systemctl daemon-reload

systemctl restart mpks
```
