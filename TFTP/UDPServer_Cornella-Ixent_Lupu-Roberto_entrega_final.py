# TFTP UDP Servidor. Ixent Cornella, Roberto Lupu

from socket import *
from struct import * 
import os.path
MODULSEQ = 65536
RTO = 1 		#RT0 per defecte



# Escollim port per conexió
serverPort = 12001


# Creem socket ipv4 UDP
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))


print ("El servidor esta llest per rebre peticions al port: " + str(serverPort))

while True:
	aux , clientAddress = serverSocket.recvfrom(1024)
	a,tipus,e,g = unpack('bbbb',aux[0:4])		# Recuperem codi
	nom_fitxer = aux[4:].decode()			# Recuperem nom fitxer
	fitxer_existent = os.path.exists('fitxers/'+nom_fitxer)
	if (tipus == 1 and fitxer_existent == False):
		print("Error: el fitxer solicitat no es troba al servidor")
		serverSocket.sendto(pack('bbbb',0,5,0,0) + "Error, fitxer no trobat al servidor".encode(), clientAddress)#ELs dos bytes de més al final son per a que tots els paquest siguin iguals en capçalera
		continue
	MSS=2**e					# Obtenim MSS i RTO
	if g==1:	
		RTO=0.5
	elif g==2:
		RTO=0.75
	elif g==3:
		RTO=1
	elif g==4:
		RTO=1.5
	elif g==5:
		RTO=2
	elif g==6:
		RTO=4
		
	if tipus == 1:
		tipus_trans = 'RRQ'			# Mirem el tipus de request
	elif tipus == 2:
		tipus_trans = 'WRQ'
	else:
		print('Error, Codi d"operació inesperat')
	print('Iniciant procés de '+tipus_trans+' amb un MSS de '+str(MSS)+'i un RTO de '+str(RTO))
	##################### WRQ ##################################
	if (tipus_trans == 'WRQ'): 
		serverSocket.sendto(pack('bbH',0,4,0), clientAddress)
		nextseq = 1
		fitxer = open(nom_fitxer,"wb")
		datasize = MSS
		paquets_rebuts = 0
		print("Rebent fitxer...")
		while datasize == MSS:			# Mentre el client encara hagi d'enviar paquets:
			codi = serverSocket.recv(MSS+4)
			if(codi[1] != 3):			# Comprovem codi de paquet correcte
				print('error, tius de paquet 	inseperat')
			tupla = (unpack('bbH', codi[0:4]))
			s_seq = tupla[2]
			if(s_seq%MODULSEQ == nextseq%MODULSEQ):	# Comprovem que numero sequencia sigui correcte
				datasize=len(codi[4:])
				fitxer.write(codi[4:])
				nextseq = nextseq + 1
				ack = pack('bbH', 0, 4, s_seq%MODULSEQ)	
				serverSocket.sendto(ack, clientAddress)	# Enviem ack
				paquets_rebuts = paquets_rebuts + 1
			else:				
				print('error, esperaba nseq = '+str(nextseq%MODULSEQ)+' i he rebut un nseq de '+str(s_seq%MODULSEQ))
			
		print('Fi de la transimissio: ' + str(paquets_rebuts-1) + ' paquets rebuts de ' + str(MSS) + ' bytes i un paquet de '+ str(datasize)+ ', sumant un total de ' + str(datasize+MSS*(paquets_rebuts-1)) + ' bytes.\n')
		fitxer.close()
	
	##################### RRQ ##################################
	elif (tipus_trans == 'RRQ'):
		fitxer = open("fitxers/"+nom_fitxer,"rb")
		ns = 1
		data=fitxer.read(MSS)
		paquets_enviats = 0
		paquets_perduts = 0
		print("Fitxer en proces d'enviarse...")
		serverSocket.sendto(pack('bbH', 0, 3, ns%MODULSEQ) +data, clientAddress)
		print('Paquet amb ns '+str(ns)+' enviat')
		
		while len(data)==MSS:		# Mentre encara quedin dades per enviar...
		
			try:			# Enviem el fitxer i esperem ACK
				serverSocket.settimeout(RTO)
				ack = serverSocket.recv(4)
				serverSocket.settimeout(None)
				c_seq = unpack('bbH', ack[0:4])
				if c_seq[1] != 4:
					print('error, capçalera inesperada: '+ str(c_seq[1]))
				if ns%MODULSEQ != c_seq[2]:	#  
					print('error, nseq del ACK no esperat. Esperat: ' + str(ns%MODULSEQ) + ' Rebut: ' + str(c_seq[2]))
				else:
					data=fitxer.read(MSS)	
					paquets_enviats = paquets_enviats + 1
					ns=ns+1
					serverSocket.sendto(pack('bbH', 0, 3, ns%MODULSEQ) +data, clientAddress)
					print('Paquet amb ns '+str(ns)+' enviat')
			except timeout:	# Si ACK incorrecte, tornem a enviar el paquet perdut, ja que es produeix timeout
				serverSocket.sendto(pack('bbH', 0, 3, ns%MODULSEQ) +data, clientAddress)
				print('Paquet amb ns '+str(ns)+' reenviat')
				paquets_perduts = paquets_perduts + 1
		while True:
			# Aquest ultim bucle es unicament per rebre l'ultim paquet ACK, que te finalitzacio implicita (pot ser que datasize < MSS).
			try:
				serverSocket.settimeout(RTO)
				ack = serverSocket.recv(4)
				serverSocket.settimeout(None)
				c_seq = unpack('bbH', ack[0:4])
				if c_seq[1] != 4:
					print('error, capçalera inesperada: '+ str(c_seq[1]))
				if ns%MODULSEQ != c_seq[2]:
					print('error, nseq del ACK no esperat. Esperat: ' + str(ns%MODULSEQ) + ' Rebut: ' + str(c_seq[2]%MODULSEQ))
				else:
					break
			except timeout:
				serverSocket.sendto(pack('bbH', 0, 3, ns%MODULSEQ) +data, clientAddress)
				print('Paquet amb ns '+str(ns)+' reenviat')
				paquets_perduts = paquets_perduts + 1
				
		print('Fi de la transimissio: ' + str(paquets_enviats) + ' paquets enviats de ' + str(MSS) + ' bytes i un paquet de '+ str(len(data))+ ', sumant un total de ' + str(len(data)+MSS*(paquets_enviats)) + ' bytes.')
		print("S'han hagut de reenviar " + str(paquets_perduts) + " paquets, deixant un total de " + str(paquets_perduts*MSS) + " bytes reenviats.\n")
		fitxer.close()
