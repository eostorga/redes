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
client_sock.settimeout(2)

def rdt_send(message_array):
    print "Entro a enviar"
    global next_seq_num, count
    # Envia solo la ventana   
    if next_seq_num < base_seq_num + window_size:
        packet = str(next_seq_num)+':'+message_array[count-1]
        client_sock.sendall(packet)
        next_seq_num = count % seq_range # Asigna el siguiente numero de secuencia
        print "Envio: "+packet+" Next seq number: "+str(next_seq_num)+" Base: "+str(base_seq_num)
        count += 1
        time.sleep(0.1)
    else:
        print "No"

def rdt_recv():
    print "Entro a recibir"
    global base_seq_num
    try:
        data = client_sock.recv(19)
    except socket.timeout, e:
        print "timeout"
        data = ""
    if data:
        ack_message = int(data)
        base_seq_num = ack_message + 1
        print "Recibo: "+data+" Next seq number: "+str(next_seq_num)+" Base: "+str(base_seq_num)

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

    while True:
        # Enviando datos 
        rdt_send(message_array)
        rdt_recv()

finally:
    print >>sys.stderr, 'Cerrando socket'
    client_sock.close()