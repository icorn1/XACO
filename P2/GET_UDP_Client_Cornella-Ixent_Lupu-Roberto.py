# GET UDP Client. Roberto Lupu, Ixent Cornella.

from socket import *

# Donem ip i port del servidor.
serverName = '192.168.1.135'
serverPort = 12005

# Demanem conexió ipv4 i UDP.
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Obtenim el nom del fitxer 
nomfitxer = input('Indique el nombre del documento que desea obtener:')

# Enviem el nom del fitxer al servidor.
clientSocket.sendto(nomfitxer.encode(),(serverName,serverPort))

# Anem escribint en un fitxer de 1024 bytes a 1024 el que ens envia el servidor.
missatge= 1
fitxer = open(nomfitxer,"wb")
while (missatge):
	missatge = clientSocket.recv(1024)
	fitxer.write(missatge)

# Fi 
clientSocket.close()
fitxer.close()
