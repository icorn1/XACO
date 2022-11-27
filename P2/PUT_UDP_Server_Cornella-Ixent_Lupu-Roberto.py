# PUT UDP Servidor. Ixent Cornella, Roberto Lupu

from socket import *

# Escollim port per conexió
serverPort = 12005


# Creem socket ipv4 UDP
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print ("El Servidor esta listo para recibir")
while True:
	# Anem rebent el fitxer de 1024 bytes a 1024 bytes.
	nomfitxer, clientAddress = serverSocket.recvfrom(1024)
	missatge = 1#serverSocket.recv(1024)
	fitxer = open(nomfitxer.decode(),"wb")
	while (missatge):
		
		missatge = serverSocket.recv(1024)
		fitxer.write(missatge)
	fitxer.close()
