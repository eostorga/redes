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
# Range = [0,seq_range]
seq_range = (window_size*2)
base_seq_num = 0
next_seq_num = 0
count = 1
acks_received = 0
message_array = []
message_length = 0
lock = threading.RLock()
start_timer = False
stop_timer = False
to_send = True
to_recv = True
stop_clock = False

# Creando el socket TCP/IP para conectarse al intermediario
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Obtiene el numero de puerto donde escucha el intermediario
port_number = int(sys.argv[3])
# Conecta el socket en el puerto cuando el intermediario este escuchando
interm_address = ('localhost', port_number)
client_sock.connect(interm_address)
#client_sock.settimeout(1)

# Abre el archivo con el mensaje a enviar y lo guarda en un arreglo
def open_file():
    global message_array
    global message_length
    with open(sys.argv[2],'r') as file_to_send:
        message = file_to_send.read()
    file_to_send.close()
    message_array = list(message)
    message_length = len(message_array)

# Crea el segmento a partir del número de secuencia y el indice del arreglo del mensaje
def make_segment(seq_num, index):
    segment = str(seq_num)+':'+message_array[index]
    return segment

def resend():
    global start_timer
    start_timer = True
    resend = base_seq_num
    index = count - 1 - window_size
    while resend < next_seq_num:
        segment = make_segment(resend, index)
        client_sock.sendall(segment)
        print "Resending segment: \""+segment+"\"."
        resend += 1
        index += 1

def timer():
    secs = 0
    while not stop_clock:
        if start_timer:
            secs = time_wait_sec
            while secs > 0 and not stop_timer:
                time.sleep(1)
                secs -= 1
            if secs == 0:
                lock.acquire()
                print "Oops, Time out!"
                resend()
                lock.release()
        elif stop_timer:
            secs = time_wait_sec           

def send_packets():
    global next_seq_num
    global count
    global start_timer
    global to_send
    # Envia solo la ventana
    while next_seq_num < base_seq_num + window_size and count <= message_length:
        lock.acquire()
        segment = make_segment(next_seq_num, count-1)
        client_sock.sendall(segment)
        if base_seq_num == next_seq_num:
            start_timer = True
        # Avanza al siguiente numero de secuencia
        next_seq_num = count % seq_range
        print "Sending segment: \""+segment+"\"."
        if count == message_length:
            to_send = False
        count += 1
        lock.release()

def rdt_send():
    while to_send:
        send_packets()
    print "No more new segments to send."

def rdt_recv():
    global base_seq_num
    global start_timer
    global stop_timer
    global acks_received
    global to_recv
    global stop_clock
    while to_recv:
        data = client_sock.recv(19)
        if data:
            ack_number = int(data)
            acks_received += 1
            print "Receiving ACK number: \""+str(ack_number)+"\"."
            base_seq_num = ack_number + 1
            if base_seq_num == next_seq_num:
                stop_timer = True
            else:
                start_timer = True
        if acks_received == message_length - 1:
            to_recv = False
            stop_clock = True
    print "All segments sent already ACKed."

def main():
    open_file()
    send_thread = threading.Thread(target=rdt_send)
    recv_thread = threading.Thread(target=rdt_recv)
    time_thread = threading.Thread(target=timer)
    send_thread.start()
    recv_thread.start()
    time_thread.start()
    send_thread.join()
    recv_thread.join()
    time_thread.join()
    print "Everything went OK! Your message has been successfully sent! :)"
    client_sock.close()
    print "Closing socket connection."

if __name__ == "__main__":
    main()
