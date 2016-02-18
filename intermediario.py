# -*- coding: utf-8 -*-
# Programa Intermediario
# Argumentos en la linea de comandos
# python [0: intermediario.py] [1: modo] [2: puerto_interm] [3: puerto_servidor] [4: probabilidad]

import socket
import sys
import time
import threading
import random
import select
import Queue

lock = threading.RLock()
probability = int(sys.argv[4]) / float(100)
mode = sys.argv[1]
inputs = []
outputs = []
message_queues = []
segments_array = []
message_queue = Queue.Queue()
more_from_client = True

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
    random.seed()
    num = random.random()
    return num <= probability

def from_client():
    global message_queue
    global more_from_client
    while more_from_client:
        data = client_connection.recv(19)
        if data:
            try:
                valid_segment = int(data[0])
                message_queue.put(data)
            except ValueError:
                iservr_sock.sendall(data)
                more_from_client = False

def to_server():
    global segments_array
    global more_from_client
    send_server = False
    while more_from_client:
        try:
            segment = message_queue.get_nowait()
            if mode == 'n':
                if segment:
                    discard = loss_segment()
                    if discard:
                        lock.acquire()
                        print >>sys.stderr, 'Segment "%s" lost.' % segment
                        lock.release()
                    elif not discard:
                        lock.acquire()
                        time.sleep(0.05)
                        iservr_sock.sendall(segment)
                        lock.release()
            elif mode == 'd':
                if segment:
                    print >>sys.stderr, 'Receiving segment: "%s"' % segment
                    discard = raw_input("Discard? (y/n): ")
                    if discard == 'y':
                        print >>sys.stderr, 'Segment "%s" lost.' % segment
                    elif discard == 'n':
                        segments_array.append(segment)
                        is_empty = message_queue.empty()
                        if is_empty:
                            send_server = True
        except Queue.Empty:
            if send_server:
                time.sleep(1)
                length = len(segments_array)
                for index in range(0, length):
                    lock.acquire()
                    time.sleep(0.05)
                    # print >>sys.stderr, 'Sending segment to server: "%s".' % segments_array[index]
                    iservr_sock.sendall(segments_array[index])
                    lock.release()
                for jndex in range(0, length):
                    lock.acquire()
                    segments_array.pop()
                    lock.release()
                send_server = False

def to_client():
    global more_from_client
    while more_from_client:
        data_from_server = iservr_sock.recv(19)
        if data_from_server:
            #if mode == 'd':
            #    print >>sys.stderr, 'Sending ACK number "%s" back to the client.' % data_from_server
            client_connection.sendall(data_from_server)

def main():
    recv_client_thread = threading.Thread(target=from_client)
    send_server_thread = threading.Thread(target=to_server)
    recv_server_thread = threading.Thread(target=to_client)
    
    recv_client_thread.start()
    send_server_thread.start()
    recv_server_thread.start()
    
    recv_client_thread.join()
    send_server_thread.join()
    recv_server_thread.join()

    print "Closing connection."
    client_connection.close()
    iclent_sock.close()
    iservr_sock.close()

if __name__ == "__main__":
    main()
