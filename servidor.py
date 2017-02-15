#!/usr/bin/env python

import socket

# Fase subscripcio

SUBS_REQ = 0x00
SUBS_ACK = 0x01
SUBS_INFO = 0x02
INFO_ACK = 0x03
SUBS_NACK = 0x4
SUBS_REJ = 0x05

# Fase client

DISCONNECTED = 0xa0
NOT_SUBSCRIBED = 0xa1
WAIT_ACK_SUBS = 0xa2
WAIT_ACK_INFO = 0xa3
SUBSCRIBED = 0xa4
SEND_HELLO = 0xa5
WAIT_INFO = 0xa6

HELLO = 0x10
HELLO_REJ = 0x11

# Tipus paquet

SEND_DATA = 0x20
SET_DATA = 0x21
GET_DATA = 0x22
DATA_ACK = 0x23
DATA_NACK = 0x24
DATA_REJ = 0x25

# Variables globals

# Variables fitxer server.cfg

name = ''
mac = ''
udp_port = ''
tcp_port = ''


def setup():
    global name
    global mac
    global udp_port
    global tcp_port

    f = open("server.cfg", "r")
    for line in f:
        tmp = line.split()
        if tmp[0].find('Name') != -1:
            name = tmp[1]
        elif tmp[0].find('MAC') != -1:
            mac = tmp[1]
        elif tmp[0].find('UDP-port') != -1:
            udp_port = tmp[1]
        elif tmp[0].find('TCP-port') != -1:
            tcp_port = tmp[1]


if __name__ == '__main__':
    setup()
    print name
    print mac
    print udp_port
    print tcp_port
