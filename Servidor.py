# -*- coding: utf-8 -*-

# Programa Servidor
import socket
import sys
 
# Creando el socket TCP/IP
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

'''
Argumentos en la linea de comandos
python [0: servidor.py] [1: modo] [2: puerto_servidor]
'''
# Obtiene el numero de puerto donde escucha el servidor
server_port = int(sys.argv[2])

# Enlace de socket y el puerto del servidor
server_address = ('localhost', server_port)
print >>sys.stderr, 'Empezando a levantar %s en el puerto %s' % server_address
server_sock.bind(server_address)

# Escuchando conexiones entrantes
server_sock.listen(1)
 
while True:
    # Esperando conexion
    print >>sys.stderr, 'Esperando para conectarse'
    connection, client_address = server_sock.accept()
 
    try:
        print >>sys.stderr, 'Conexion desde', client_address
 
        # Recibe los datos en trozos y reetransmite
        while True:
            data = connection.recv(1000)
            if data:
                print >>sys.stderr, 'Recibido "%s"' % data
                print >>sys.stderr, 'Enviando mensaje de vuelta al cliente'
                connection.sendall(data)
            else:
                print >>sys.stderr, 'No hay mas datos', client_address
                break
             
    finally:
        # Cerrando conexion
        connection.close()
