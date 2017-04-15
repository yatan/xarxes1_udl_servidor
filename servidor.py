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
import socket
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

options = []

# Variables fitxer server.cfg

name = ''
mac = ''
udp_port = ''
tcp_port = ''

list_controlers = []


class Controlador:
    name = ""
    mac = ""
    status = DISCONNECTED

    def __init__(self, nom, macdrr):
        """
        Generar un nou Controlador a partir del nom i mac
        :param nom:
        :param macdrr:
        """
        self.name = nom
        self.mac = macdrr

    def __str__(self):
        return str(self.name) + " " + str(self.mac)

    def __repr__(self):
        return str(self.name) + " " + str(self.mac) + " Estat: " + str(self.status) + "\n"

    # Comparador entre 2 controladors siguin iguals (nom i situacio)
    def __cmp__(self, other):
        if self.name == other.name and self.mac == other.mac:
            return 0
        else:
            return 1


estatactiu = DISCONNECTED


def enviarUDP(sockt, thread, tipus, maca, aleat, dades):
    """
    Funcio per enviar trama UDP
    :param sockt: 
    :param thread: 
    :param tipus: 
    :param maca: 
    :param aleat: 
    :param dades: 
    """
    cosa = pack('B13s9s80s', tipus, maca, aleat, dades)
    sockt.sendto(cosa, thread.client_address)


def parserdata(resposta, sockt, thread):
    rebut = unpack('B13s9s80s', resposta)
    trama = []
    paquet = {'tipus': 0x00, 'MAC': "", 'alea': 0, 'dades': ""}
    # print rebut
    for element in rebut:
        trama.append(str(element).split('\x00')[0])

    paquet['tipus'] = hex(int(trama[0]))
    paquet['MAC'] = trama[1]
    paquet['alea'] = trama[2]
    paquet['dades'] = trama[3]
    # Analitzar les dades del paquet rebut
    if paquet['tipus'] == hex(SUBS_REQ):
        if options.debug:
            print "SUBS_REEREQQQ"
        # En cas de SUBS_REQ, verificar que la mac i
        # el nom del controlador estan a la llista, i verificar
        # que aleatori = 00000, guardar la situacio de les dades
        controladorrebut = paquet['dades'].split(",")
        controladorrebut = Controlador(controladorrebut[0], paquet['MAC'])

        if controladorrebut in list_controlers:
            enviarUDP(sockt, thread, SUBS_ACK, mac, '000000', "6667")  # \.... Dades amb port udp aleatori
            controladorrebut.status = WAIT_ACK_INFO
            t = threading.Thread(target=filudp())
            t.start()

            if options.debug:
                print "Acceptat - El controlador esta a la llista de controladors valids"
        else:
            enviarUDP(sockt, thread, SUBS_REJ, paquet['MAC'], paquet['alea'], "Controlador no esta a la llista")
            if options.debug:
                print "El controlador no esta a la llista de controladors"

    elif paquet['tipus'] == hex(HELLO):
        print "HELOLLOLO"
        cosa = pack('B13s9s80s', HELLO, mac, '000000', '6565')
        sockt.sendto(cosa, thread.client_address)

    else:
        print "UNKNOWN paquet " + paquet['tipus']


def filudp(port=6667):
    """
    Fil on es creara un servei udp per escoltar les
     dades desde un port especificat per nosaltres.    
    :param port: 
    """
    UDP_IP = "localhost"

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, port))

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        rebut = unpack('B13s9s80s', data)
        trama = []
        paquet = {'tipus': 0x00, 'MAC': "", 'alea': 0, 'dades': ""}
        # print rebut
        for element in rebut:
            trama.append(str(element).split('\x00')[0])

        paquet['tipus'] = hex(int(trama[0]))
        paquet['MAC'] = trama[1]
        paquet['alea'] = trama[2]
        paquet['dades'] = trama[3]
        print "received message from port: " + str(port) + " : ", paquet


class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # print vars(self)
        data = self.request[0].strip()
        sockt = self.request[1]
        parserdata(data, sockt, self)

        # get port number
        # port = self.client_address[1]
        # get the communicate socket
        # get client host ip address
        # client_address = (self.client_address[0])
        # proof of multithread
        # cur_thread = threading.current_thread()
        # print "thread %s" % cur_thread.name
        # print "received call from client address :%s" % client_address
        # print "received data from port [%s]: %s" % (port, data)

        # assemble a response message to client
        # response = "%s %s" % (cur_thread.name, data)
        # socket.sendto(response.upper(), self.client_address)


class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass


def setup():
    global name
    global mac
    global udp_port
    global tcp_port
    global options

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
    parser.add_option('-d', '--debug', action='store_true', default=False, help='debug output')
    parser.add_option('-c', '--clientfile', action='store', default="client.cfg",
                      help='Client settings, default client.cfg')
    # parser.add_option('-d', '--destination', action='store', default="127.0.0.1", help='Listening port, default 1234')
    (options, args) = parser.parse_args()
    if len(args) > 0: parser.error('bad args, use --help for help')
    # Lectura dades configuracio
    setup()
    if options.debug:
        print name
        print mac
        print udp_port
        print tcp_port
    # Lectura fitxer controladors
    readcontrollers()

    if options.debug:
        print "Llista controladors:", list_controlers

    # Threaded server
    HOST, PORT = "localhost", int(udp_port)

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
