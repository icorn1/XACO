# TCP server GET
from socket import *

# Escollim el port del servidor
serverPort = 8083

# Demanem comunicació ipv4 i TCP
serverSocket = socket(AF_INET,SOCK_STREAM)

# Ajustem el servidor 
serverSocket.bind(('',serverPort))

# Comença a rebre el servidor.
serverSocket.listen(1)
print ('El Servidor esta listo para recibir peticiones')
while True:
	# Acceptem conexió i obtenim el nom del fitxer a "donar" al client
	connectionSocket, addr = serverSocket.accept()
	nomfitxer = "fitxers/"+connectionSocket.recv(1024).decode()
	fitxer = open(nomfitxer,"rb")
	
	# Enviem el fitxer de 1024 bytes a 1024 bytes
	missatge = fitxer.read(1024)
	while (missatge):
		connectionSocket.send(missatge)
		missatge = fitxer.read(1024)
	connectionSocket.close()
	fitxer.close()
