# GET UDP Servidor. Roberto Lupu, Ixent Cornella.

from socket import *

# Escollim port per conexió
serverPort = 12005


# Creem un socket ipv4 amb UDP
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))


print ("El Servidor esta listo para recibir")
while True:
	
	# Obrim el fitxer desitjat.
	nomfitxer, clientAddress = serverSocket.recvfrom(1024)
	fitxer = open("fitxers/"+nomfitxer.decode(),"rb")
	# Enviem el fitxer de 1024 bytes a 1024 bytes fins acabar. 
	missatge = fitxer.read(1024)
	while (missatge):
		serverSocket.sendto(missatge,clientAddress)
		missatge = fitxer.read(1024)
	clientSocket.sendto("FI".encode(),clientAddress)
	fitxer.close()
