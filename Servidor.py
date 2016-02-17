# -*- coding: utf-8 -*-
# Programa Servidor
# Argumentos en la linea de comandos
# python [0: servidor.py] [1: modo] [2: puerto_servidor]  

import socket
import sys
import time
import threading

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
ack_num = 0
ack_aux = ''
message_array = []
message = ''
message_to_write = ''
interm_connection, interm_address = server_sock.accept()




def open_file(str):
    global message
    global message_length
    with open('messageServer.txt','w') as file_to_write:
		file_to_write.write( message) 
		
		if mode == 'd':
			
			print "Escrbiendo datos en el archivo"	
		

def conexion():

	global prev_ack
	global message
	global ack_num
	global ack_aux
	

	# Recibe los datos en trozos y reetransmite
	while True:
		data = interm_connection.recv(19)
		if data:
			if mode == 'd':
				print >>sys.stderr, 'Receiving segment: "%s".' % data
			data = list(data)
			
			try:
				x = 0
				ack_aux = ''
				while data[x] != ':':
					
					
					ack_aux += data[x]
					ack_num = int(ack_aux)
					x += 1

				
			
			except ValueError:
				message = ''.join(message_array)
				print >>sys.stderr, "Message received: '%s'" % message
				open_file(message)
				
			if ack_num-1 == prev_ack:
				time.sleep(0.1)
				
				y = 0
				while data[y] != ':':
					y += 1 
				if data[y+1] != '\n':	
					message_array.append(data[y+1])
				
				if mode == 'd':
					print >>sys.stderr, "Arreglo %s" % message_array

				
				if mode == 'd':
					print >>sys.stderr, 'Sending ACK number: "%s".' % ack_num
				interm_connection.sendall(str(ack_num))
				prev_ack = ack_num
	         
	
def main():

	print "Recibiendo datos"
	recv_thread = threading.Thread(target=conexion)
	recv_thread.start()
	recv_thread.join()
	print "Closing connection."
	interm_connection.close()
	server_sock.close()

if __name__ == "__main__":
    main()

	

		
