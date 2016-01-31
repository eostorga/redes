# -*- coding: utf-8 -*-

# Programa Cliente
import socket
import sys
 
# Creando el socket TCP/IP para conectarse al intermediario
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
'''
Argumentos en la linea de comandos
python [0: cliente.py] [1: modo] [2: archivo] [3: puerto] [4: ventana] [5: timeout]
'''
# Obtiene el numero de puerto donde escucha el intermediario
port_number = int(sys.argv[3])

# Conecta el socket en el puerto cuando el intermediario este escuchando
interm_address = ('localhost', port_number)
print >>sys.stderr, 'Conectando a %s en el puerto %s' % interm_address
client_sock.connect(interm_address)

try:     
    # Enviando datos
    with open(sys.argv[2],'r') as file_to_send:
        message = file_to_send.read()
    file_to_send.close()

    print >>sys.stderr, 'Enviando "%s"' % message
    client_sock.sendall(message)
 
    # Buscando respuesta
    amount_received = 0
    amount_expected = len(message)
     
    while amount_received < amount_expected:
        data = client_sock.recv(19)
        amount_received += len(data)
        print >>sys.stderr, 'Recibiendo "%s"' % data
 
finally:
    print >>sys.stderr, 'Cerrando socket'
    client_sock.close()