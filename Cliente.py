# -*- coding: utf-8 -*-
# Programa Cliente
# Argumentos en la linea de comandos
# python [0: cliente.py] [1: modo] [2: archivo] [3: puerto] [4: ventana] [5: timeout]

import socket
import sys
import time
import threading
import signal

# Variables globales
window_size = int(sys.argv[4])
# Tiempo a esperar para timeout en milisegundos y segundos
time_wait_mse = int(sys.argv[5])
time_wait_sec = time_wait_mse / 1000
# Window size <= sequence range/2
seq_range = (window_size*2) # range = [0,seq_range]
base_seq_num = 0
next_seq_num = 0
count = 1
message_array = []
lock = threading.RLock()
start_timer = False
stop_timer = False

# Creando el socket TCP/IP para conectarse al intermediario
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Obtiene el numero de puerto donde escucha el intermediario
port_number = int(sys.argv[3])
# Conecta el socket en el puerto cuando el intermediario este escuchando
interm_address = ('localhost', port_number)
client_sock.connect(interm_address)
#client_sock.settimeout(1)

def open_file():
    with open(sys.argv[2],'r') as file_to_send:
        message = file_to_send.read()
    file_to_send.close()
    # Separa la string en un arreglo de caracteres y envia uno a uno al servidor
    return list(message);

def resend():
    global start_timer
    resend = base_seq_num
    index = count - 1 - window_size
    while resend < next_seq_num:
        packet = str(resend)+':'+message_array[index]
        client_sock.sendall(packet)
        print "Envio: "+packet
        resend += 1
        index += 1
    start_timer = True

def timeout():
    secs = 0
    while True:
        if start_timer:
            secs = time_wait_sec
            while secs > 0 and not stop_timer:
                time.sleep(1)
                secs -= 1
            if secs == 0:
                lock.acquire()
                resend()
                lock.release()
        elif stop_timer:
            secs = time_wait_sec           

def send_packets():
#def rdt_send():
    global next_seq_num
    global count
    global start_timer
    # Envia solo la ventana
    while next_seq_num < base_seq_num + window_size:
        lock.acquire()
        packet = str(next_seq_num)+':'+message_array[count-1]
        client_sock.sendall(packet)
        if base_seq_num == next_seq_num:
            start_timer = True
        next_seq_num = count % seq_range # Asigna el siguiente numero de secuencia
        print "Envio: "+packet+" Next seq number: "+str(next_seq_num)+" Base: "+str(base_seq_num)
        count += 1
        lock.release()

def rdt_send():
    while True:
        send_packets()

def rdt_recv():
    while True:
        global base_seq_num
        global start_timer
        global stop_timer
        data = client_sock.recv(19)
        if data:
            ack_message = int(data)
            base_seq_num = ack_message + 1
            print "Recibo: "+data+" Next seq number: "+str(next_seq_num)+" Base: "+str(base_seq_num)
            if base_seq_num == next_seq_num:
                stop_timer = True
            else:
                start_timer = True

def main():
    global message_array
    message_array = open_file()
    
    threading.Thread(target=rdt_recv).start()
    threading.Thread(target=rdt_send).start()
    threading.Thread(target=timeout).start()
    # client_sock.close()

if __name__ == "__main__":
    main()
