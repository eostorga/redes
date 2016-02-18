# -*- coding: utf-8 -*-
# Programa Servidor
# Argumentos en la linea de comandos
# python [0: servidor.py] [1: modo] [2: puerto_servidor]  

import socket
import sys
import time
import threading

mode = sys.argv[1]
prev_ack = -1
ack_num = 0
ack_aux = ''
message_array = []
message = ''
message_to_write = ''
more_from_client = True
lock = threading.RLock()

# Creando el socket TCP/IP
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Obtiene el numero de puerto donde escucha el servidor
server_port = int(sys.argv[2])
# Enlace de socket y el puerto del servidor
server_address = ('localhost', server_port)
server_sock.bind(server_address)
# Escuchando conexiones entrantes
server_sock.listen(1)

interm_connection, interm_address = server_sock.accept()

def open_file(str):
    global message
    global message_length
    with open('messageServer.txt','w') as file_to_write:
		file_to_write.write(message) 		
		if mode == 'd':
			print "Writing file..."	
		
def connection():
	global prev_ack
	global message
	global ack_num
	global ack_aux
	global more_from_client
	# Recibe los datos en trozos y reetransmite
	while more_from_client:
		data = interm_connection.recv(19)
		if data:
			data_array = list(data)
			try:
				x = 0
				ack_aux = ''
				while data_array[x] != ':':
					ack_aux += data_array[x]
					ack_num = int(ack_aux)
					x += 1
				if mode == 'd':
					print >>sys.stderr, 'Receiving segment: "%s".' % data
			except ValueError:
				message = ''.join(message_array)
				print >>sys.stderr, "Message received: '%s'" % message
				open_file(message)
				more_from_client = False
			if ack_num-1 == prev_ack:
				y = 0
				while data_array[y] != ':':
					y += 1 
				if data_array[y+1] != '\n':	
					message_array.append(data_array[y+1])
				if mode == 'd':
					print >>sys.stderr, "Message: %s." % message_array
				lock.acquire()
				if mode == 'd':
					print >>sys.stderr, 'Sending ACK number: "%s".' % ack_num
				interm_connection.sendall(str(ack_num))
				time.sleep(0.03)
				lock.release()
				prev_ack = ack_num

def main():
	recv_thread = threading.Thread(target=connection)
	recv_thread.start()
	recv_thread.join()
	print "Closing connection."
	interm_connection.close()
	server_sock.close()

if __name__ == "__main__":
    main()
