# PUT TCP Client. Ixent Cornella, Roberto Lupu
import sys
from socket import *

# Donem ip i port del servidor.
serverName = 'localhost'
serverPort = 8084

# Demanem conexió ipv4 i TCP.
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

# Obtenim nom del fitxer a guardar al servidor i l'enviem
nomfitxer = input('Indique el nombre del documento que desea enviar:') 
clientSocket.send(nomfitxer.encode())

# Obrim i enviem el fitxer de 1024 bytes a 1024 bytes
fitxer = open("fitxers/"+nomfitxer,"rb")
missatge = fitxer.read(1024)
while (missatge):
	clientSocket.send(missatge)
	missatge = fitxer.read(1024)

clientSocket.close()
fitxer.close()
