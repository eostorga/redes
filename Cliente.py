# -*- coding: utf-8 -*-
# Programa Cliente
# Argumentos en la linea de comandos
# python [0: cliente.py] [1: modo] [2: archivo] [3: puerto] [4: ventana] [5: timeout]

import socket
import sys
import time
 
# Creando el socket TCP/IP para conectarse al intermediario
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Obtiene el numero de puerto donde escucha el intermediario
port_number = int(sys.argv[3])
# Conecta el socket en el puerto cuando el intermediario este escuchando
interm_address = ('localhost', port_number)
client_sock.connect(interm_address)

def rdt_send(message_array):
    global next_seq_num, count
    # Envia solo la ventana 
    while next_seq_num < base_seq_num + window_size:
        packet = str(next_seq_num)+':'+message_array[next_seq_num]
        client_sock.sendall(packet)
        next_seq_num = count % seq_range # Asigna el siguiente numero de secuencia
        count += 1
        time.sleep(0.1)

def rdt_recv():

def open_file():
    with open(sys.argv[2],'r') as file_to_send:
        message = file_to_send.read()
    file_to_send.close()
    # Separa la string en un arreglo de caracteres y envia uno a uno al servidor
    return list(message);

try:
    message_array = open_file()
    window_size = int(sys.argv[4])
    time_to_wait = int(sys.argv[5])
    # Window size <= sequence range/2
    seq_range = (window_size*2) # range = [0,seq_range]
    base_seq_num = 0
    next_seq_num = 0
    count = 1

    # Enviando datos 
    rdt_send(message_array)

    data = client_sock.recv(1000)
    print >>sys.stderr, 'Recibiendo %s' % data

finally:
    print >>sys.stderr, 'Cerrando socket'
    client_sock.close()