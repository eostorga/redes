# -*- coding: utf-8 -*-
# Programa Intermediario
# Argumentos en la linea de comandos
# python [0: intermediario.py] [1: modo] [2: puerto_interm] [3: puerto_servidor] [4: probabilidad]

import socket
import sys
import time
 
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
 
while True:
    # Esperando conexion
    connection, client_address = iclent_sock.accept()
 
    try:
        # Recibe los datos en trozos y reetransmite
        while True:
            data = connection.recv(1000)
            if data:
                print >>sys.stderr, 'Recibido "%s"' % data
                iservr_sock.sendall(data)
            else:
                print >>sys.stderr, 'No hay mas datos', client_address
                break

            data_from_server = iservr_sock.recv(100)
            if data_from_server:
                print >>sys.stderr, 'Enviando mensaje de vuelta al cliente "%s"' % data_from_server
                connection.sendall(data_from_server)
             
    finally:
        # Cerrando conexion
        connection.close()
