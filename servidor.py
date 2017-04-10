#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

"""
SYNOPSIS

    client.py [-h,--help] [--version] [c, --clientfile <port>, default=1234]
        [-d, --destination <address>, default=127.0.0.1]

DESCRIPTION

    Creates a ECHO/UDP client, connects to server, sends data and
    prints the returned data.
    Default port 1234, default address=127.0.0.1


EXAMPLES

    client.py  -h

AUTHOR

    Francisco Romero Batalle <frb2@alumnes.udl.cat>

LICENSE

    This script is published under the Gnu Public License GPL3+

VERSION

    0.0.1
"""

import SocketServer
import optparse
import threading
from struct import *

__program__ = "client"
__version__ = '0.0.1'
__author__ = 'Francisco Romero Batalle <frb2@alumnes.udl.cat>'
__copyright__ = 'Copyright (c) 2016  Francisco Romero Batalle'
__license__ = 'GPL3+'
__vcs_id__ = '$Id: client.py 554 2012-05-06 08:07:51Z frb2 $'

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

list_controlers = []


def printardata(resposta):
    rebut = unpack('B13s9s80s', resposta)
    trama = []
    paquet = {'tipus': 0x00, 'MAC': "", 'alea': 0, 'dades': ""}
    # print rebut
    for element in rebut:
        trama.append(str(element).split('\x00')[0])

    paquet['tipus'] = hex(int(trama[0]));
    paquet['MAC'] = trama[1];
    paquet['alea'] = trama[2];
    paquet['dades'] = trama[3];
    print paquet


class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        # get port number
        port = self.client_address[1]
        # get the communicate socket
        socket = self.request[1]
        # get client host ip address
        client_address = (self.client_address[0])
        # proof of multithread
        cur_thread = threading.current_thread()
        print "thread %s" % cur_thread.name
        print "received call from client address :%s" % client_address
        print "received data from port [%s]: %s" % (port, data)
        printardata(data)

        # assemble a response message to client
        response = "%s %s" % (cur_thread.name, data)
        socket.sendto(response.upper(), self.client_address)


class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass


class Controlador:
    name = ""
    mac = ""

    def __init__(self, nom, macdrr):
        self.name = nom
        self.mac = macdrr

    def __str__(self):
        return str(self.name) + " " + str(self.mac)

    def __repr__(self):
        return str(self.name) + " " + str(self.mac)


def setup():
    global name
    global mac
    global udp_port
    global tcp_port

    try:
        f = open("server.cfg", "r")
        for line in f:
            if line not in ['\n', '\r\n']:
                tmp = line.split()
                if tmp[0].find('Name') != -1:
                    name = tmp[2]
                elif tmp[0].find('MAC') != -1:
                    mac = tmp[2]
                elif tmp[0].find('UDP-port') != -1:
                    udp_port = tmp[2]
                elif tmp[0].find('TCP-port') != -1:
                    tcp_port = tmp[2]
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except ValueError:
        print "Could not convert data to an integer."
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise


def readcontrollers():
    try:
        f = open("controlers.dat", "r")
        for line in f:
            if line not in ['\n', '\r\n']:
                tmp = line.replace('\n', '').replace(' ', '').split(',')
                list_controlers.append(Controlador(tmp[0], tmp[1]))

    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except ValueError:
        print "Could not convert data to an integer."
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise


if __name__ == '__main__':
    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()["__doc__"],
                                   version=__version__)
    parser.add_option('-v', '--verbose', action='store_true', default=False, help='verbose output')
    parser.add_option('-c', '--clientfile', action='store', default="client.cfg",
                      help='Client settings, default client.cfg')
    parser.add_option('-d', '--destination', action='store', default="127.0.0.1", help='Listening port, default 1234')
    (options, args) = parser.parse_args()
    if len(args) > 0: parser.error('bad args, use --help for help')

    setup()
    print name
    print mac
    print udp_port
    print tcp_port
    readcontrollers()
    print list_controlers

    HOST, PORT = "localhost", 2345

    server = ThreadedUDPServer((HOST, PORT),
                               ThreadedUDPRequestHandler)
    ip, port = server.server_address
    server.serve_forever()
    # Start a thread with the server --
    # that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    server.shutdown()
