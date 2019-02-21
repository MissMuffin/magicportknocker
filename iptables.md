# Iptables setup

### 1. Allow ssh
```
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
sudo iptables -A OUTPUT -p tcp --sport 22 -m conntrack --ctstate ESTABLISHED -j ACCEPT
```

### 2. Allow loopback connections (localhost)
```
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT
```

### 3. Allow established tcp connections
```
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

### 4. Allow outgoing udp
```
sudo iptables -A INPUT -p udp --sport 53 -m state --state ESTABLISHED -j ACCEPT
```

### 5. Open UDP input port for auth (13337)
```
sudo iptables -A INPUT -p udp -m udp --dport 13337 -j ACCEPT
```

### 6. Set policy to drop
```
sudo iptables -P INPUT DROP
```


## Persistent setup

Install iptables-persistent
```
apt install iptables-persistent
```

IPv4 and IPv6 rules can be saved to the following files during installation. These files will then be loaded into iptables on system start up.

To add new rules to be loaded on startup save new rules to `/etc/iptables/rules.v4` and `/etc/iptables/rules.v6` first add the rules with the ```iptables``` command and then save via 
```
iptables-save > /etc/iptables/rules.v4
```
and
``` 
ip6tables-save > /etc/iptables/rules.v6
```

or copy the output of ```iptables-save``` abd ```ip6tables-save``` to the corresponding files.

## Restore setup (close all client connections)
see [/scripts/iptables-reset](https://github.com/MissMuffin/magicportknocker/blob/master/scripts/iptables-reset)
```
iptables-restore </etc/iptables/rules.v4
ip6tables-restore </etc/iptables/rules.v6
```