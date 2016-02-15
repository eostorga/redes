# -*- coding: utf-8 -*-
# Programa Intermediario
# Argumentos en la linea de comandos
# python [0: intermediario.py] [1: modo] [2: puerto_interm] [3: puerto_servidor] [4: probabilidad]

import socket
import sys
import time
import threading
import random

lock = threading.RLock()
probability = int(sys.argv[4]) / 100

# Creando el socket TCP/IP para escuchar al cliente
iclent_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Creando el socket TCP/IP para conectarse al servidor
iservr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Obtiene el numero de puerto donde escucha el intermediario
interm_port = int(sys.argv[2])
# Obtiene el numero de puerto donde se conecta con el servidor
server_port = int(sys.argv[3])

# Enlace de socket y el puerto del intermediario
interm_address = ('localhost', interm_port)
# Enlace de socket y el puerto del servidor
server_address = ('localhost', server_port)
iclent_sock.bind(interm_address)
iservr_sock.connect(server_address)

# Escuchando conexiones entrantes
iclent_sock.listen(1)

client_connection, client_address = iclent_sock.accept()

def loss_segment():
    return random.random() <= probability

def to_server():
    while True:
        data = client_connection.recv(19)
        if data:
            lock.acquire()
            print >>sys.stderr, 'Receiving segment: "%s"' % data
            discard = loss_segment()
            if discard:
                print >>sys.stderr, 'Segment "%s" lost.' % data
                lock.release()
            elif not discard:
                time.sleep(0.1)
                print >>sys.stderr, 'Sending segment to server: "%s"' % data
                iservr_sock.sendall(data)
                lock.release()

def to_client():
    while True:
        data_from_server = iservr_sock.recv(19)
        if data_from_server:
            lock.acquire()
            time.sleep(0.1)
            print >>sys.stderr, 'Sending ACK number "%s" back to the client.' % data_from_server
            client_connection.sendall(data_from_server)
            lock.release()

def main():
    send_thread = threading.Thread(target=to_server)
    recv_thread = threading.Thread(target=to_client)
    send_thread.start()
    recv_thread.start()
    send_thread.join()
    recv_thread.join()
    print "Closing connection."
    client_connection.close

if __name__ == "__main__":
    main()
