# PUT UDP Client Ixent Cornella, Roberto Lupu

from socket import *

# Escollim ip i conexió del servidor
serverName = '192.168.1.135'
serverPort = 12005

# Demanem conexió UDP i IPv4
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Obtenim nom del fitxer i l'enviem al servidor
nomfitxer = input('Indique el nombre del documento que desea enviar:')
clientSocket.sendto(nomfitxer.encode(),(serverName,serverPort))


# Obrim i enviem el fitxer de 1024 bytes a 1024 bytes.
fitxer = open("fitxers/"+nomfitxer,"rb")
missatge = fitxer.read(1024)
while (missatge):
	clientSocket.sendto(missatge,(serverName,serverPort))
	missatge = fitxer.read(1024)
clientSocket.sendto("FI".encode(),(serverName,serverPort))

clientSocket.close()
fitxer.close()
