# PUT TCP Servidor. Ixent Cornella, Roberto Lupu
from socket import *

# Escollim port per conexió
serverPort = 8084

# Demanem conexió ipv4 amb TCP
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))

# Permitim  rebre peticions...
serverSocket.listen(1)
print ('El Servidor esta listo para recibir peticiones')
while True:
	# Obtenim nom del fitxer a guardar...
	connectionSocket, addr = serverSocket.accept()
	nomfitxer = connectionSocket.recv(1024).decode()
	fitxer = open(nomfitxer,"wb")

	# Guardem el fitxer de 1024 bytes a 1024 bytes.
	missatge = connectionSocket.recv(1024)
	while (missatge):
		fitxer.write(missatge)
		missatge = connectionSocket.recv(1024)
	connectionSocket.close()
	fitxer.close()
