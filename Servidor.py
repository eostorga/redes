# -*- coding: utf-8 -*-
# Programa Servidor
# Argumentos en la linea de comandos
# python [0: servidor.py] [1: modo] [2: puerto_servidor]

import socket
import sys
import time

# Creando el socket TCP/IP
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Obtiene el numero de puerto donde escucha el servidor
server_port = int(sys.argv[2])
# Enlace de socket y el puerto del servidor
server_address = ('localhost', server_port)
server_sock.bind(server_address)
# Escuchando conexiones entrantes
server_sock.listen(1)

mode = sys.argv[1]
prev_ack = -1
message_array = []

while True:
    # Esperando conexion
    connection, client_address = server_sock.accept() 
    try:
        # Recibe los datos en trozos y reetransmite
        while True:
            data = connection.recv(19)
            if data:
                try:
                    ack_num = int(data[0])
                    if mode == 'd':
                        print >>sys.stderr, 'Receiving segment: "%s".' % data
                        data = list(data)
                    if ack_num-1 == prev_ack:
                        time.sleep(0.05)
                        message_array.append(data[2])
                        if mode == 'd':
                            print >>sys.stderr, 'Sending ACK number: "%s".' % ack_num
                        connection.sendall(str(ack_num))
                        prev_ack = ack_num
                except ValueError:
                    message = ''.join(message_array)
                    print >>sys.stderr, 'Message received: "%s"' % message
            else:
                if mode == 'd':
                    print >>sys.stderr, 'No more data', client_address
                break             
    finally:
        # Cerrando conexion
        connection.close()