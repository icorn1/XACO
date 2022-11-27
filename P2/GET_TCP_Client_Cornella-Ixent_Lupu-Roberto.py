# Example d'un programa que mitjançant TCP demana l'arxiu a obtenir
import sys
from socket import *

# Obtenim la ip d'on volem obtenir el fitxer, així com el port.
serverName = '192.168.1.135'
serverPort = 8083

# Demanem comunicació IPv4 i TCP 
clientSocket = socket(AF_INET, SOCK_STREAM)

# Obrim la conexió TCP al servidor i port 
clientSocket.connect((serverName,serverPort))

# Obtenim el nom del fitxer 
nomfitxer = input('Indique el nombre del documento que desea obtener: ')

# Enviem el nom del fitxer al servidor i esperem resposta.
clientSocket.send(nomfitxer.encode())

# Creem un fitxer si no existia amb nomfitxer.
fitxer = open(nomfitxer,"wb")

# Obtenim el missatge de 1024 bytes a 1024 bytes.
missatge = clientSocket.recv(1024)
while (missatge):
	fitxer.write(missatge)
	missatge = clientSocket.recv(1024)
	if (missatge == -1): 
		break

# Tanquem socket i fitxer.
clientSocket.close()
fitxer.close()
