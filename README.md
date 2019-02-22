# Magic Portknocker

Like a portknocker but not. Magical.

Contains server and client programm as well as CLI for administrative functions. Server drops all incomming traffic except UDP traffic on authentication port. Authenticated users' IPs are whitelisted for predetemined port privileges.

This project was created for an independent course work (ICW) at the [University of Applied Sciences Berlin (HTW)](https://www.htw-berlin.de/) during the Applied Computer Science (MA) degree programm.

[💡 For extensive step by step instructions click here 💡](https://github.com/MissMuffin/magicportknocker/blob/master/instructions.md)

## Description

For an extensive write-up of the project and its inner workings/specification, see [here](https://github.com/MissMuffin/magicportknocker/blob/master/specification.md)

## Install
Either download/clone repo and then
```
python3 setup.py install
```
or install straight from github
```
pip3 install -U --user "git+https://github.com/MissMuffin/magicportknocker#egg=port-knocker"
```

## Iptables Setup
See [here](https://github.com/MissMuffin/magicportknocker/blob/master/iptables.md)

## Things to run
```portknock-admin --help```

```portknock-server --help```

```portknock-client --help```
