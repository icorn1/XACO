# TFTP UDP Client. Ixent Cornella, Roberto Lupu
###Fallito: no se contempla que el request o el ack del request no llegue
from socket import *
from struct import *
import math 
import inquirer
import os.path

MODULSEQ = 65536
serverName = 'localhost'
serverPort = 12001
MSS = 512	# opcions estandards
RTO = 3
aux=0

# Demanem conexió ipv4 i UDP.
clientSocket = socket(AF_INET, SOCK_DGRAM)
print('Client preparat per enviar/rebre dades de ' + serverName + ', al port: ' + str(serverPort) + "\n")

# Obtenim el nom del fitxer 
nom_fitxer = input('Indiqueu el nom del fitxer: ')

# Demanem mida i tipus de transmissio.


typeQuestion = [
  inquirer.List('type',
                message="Vol Enviar o rebre el fitxer? ",
                choices=['Enviar (WRQ)','Rebre (RRQ)'],
            ),]
typeAnswer = inquirer.prompt(typeQuestion)
if typeAnswer["type"]=='Enviar (WRQ)':
	tipusTrans=2
	fitxer_existent = os.path.exists('fitxers/'+nom_fitxer)
	if fitxer_existent == False:
		print('Error, fitxer "' + nom_fitxer + '" no trobat.')
		quit()
else:
	tipusTrans=1


while True:			# Aquest bucle es trencara quan l'usuari no vulgui negociar mes
	negociOpcions = [
	  inquirer.List('type',
		        message="Vol negociar alguna opció extra? ",
		        choices=['No', 'Blocksize (MSS)', 'Timeout'],
		    ),]
	negociOpcionsAns = inquirer.prompt(negociOpcions)
		 
	if negociOpcionsAns["type"]=='No':
	
		if tipusTrans==2:
			while True:
				clientSocket.sendto(pack('bbbb', 0, tipusTrans,int(math.log2(MSS)),aux) + nom_fitxer.encode(),
					     (serverName,serverPort))
				print('petició enviada')
				try:
					clientSocket.settimeout(RTO)
					ack = clientSocket.recv(4)
					clientSocket.settimeout(None)
					c_seq = unpack('bbH', ack[0:4])
					if c_seq[1] != 4:
						print('error, capçalera inesperada: '+ str(c_seq[1]))
					if 0 != c_seq[2]:
						print('error, nseq del ACK no esperat. Esperat: 0 Rebut: ' + str(c_seq[2]))
					else:
						break
				except timeout:
					print('No hem rebut el primer ack, tornem a enviar la request')
		elif tipusTrans==1:
			while True:
				clientSocket.sendto(pack('bbbb', 0, tipusTrans,int(math.log2(MSS)),aux) + nom_fitxer.encode(),
					     (serverName,serverPort))
				print('petició enviada')
				try:
					clientSocket.settimeout(RTO)
					codi = clientSocket.recv(4+MSS)
					clientSocket.settimeout(None)
					c_seq = unpack('bbH', codi[0:4])
					if c_seq[1] != 3:
						print('error, capçalera inesperada: '+ str(c_seq[1]))
					if c_seq[1]==5:
						print('El servidor ha retornat un error. Missatge d error: ')
						print(codi[2:].decode())
						quit()
					if 1 != c_seq[2]:
						print('error, nseq del ACK no esperat. Esperat: 1 Rebut: ' + str(c_seq[2]))
					else:
						fitxer = open(nom_fitxer,"wb")
						fitxer.write(codi[4:])
						ack = pack('bbH', 0, 4, 1)
						clientSocket.sendto(ack, (serverName,serverPort))
						print("Rebent fitxer...")
						print('paquet amb nseq 1 rebut')
						break

				except timeout:
					print('No hem rebut el primer paquet de dades, tornem a enviar la request')	
		break;
	elif negociOpcionsAns["type"]=='Blocksize (MSS)':
		sizeQuestion = [
		inquirer.List('size',
				message="Indiqueu el MSS: ",
				choices=[32, 64, 128, 256, 512, 1024, 2048],
			    ),]
		sizeAnswer = inquirer.prompt(sizeQuestion)
		MSS = sizeAnswer["size"]
	else:
		RTOQuestion = [
		inquirer.List('rto',
				message="Indiqueu el Timeout (en segons): ",
				choices=['0.5', '0.75', '1', '1.5', '2', '4'],
			    ),]
		RTOAnswer = inquirer.prompt(RTOQuestion)
		RTO = float(RTOAnswer["rto"])
		if RTO==0.5:
			aux=1
		elif RTO==0.75:
			aux=2
		elif RTO==1:
			aux=3
		elif RTO==1.5:
			aux=4
		elif RTO==2:
			aux=5
		elif RTO==4:
			aux=6
       

# Fins aqui l'unic que hem fet es enviar el paquet de Request amb les opcions, ara comença la transmissio
paquets_rebuts = 0
paquets_enviats = 0
paquets_perduts = 0

################### RRQ #######################
if (tipusTrans == 1): 
	nextseq = 2	#estava a 1 però el primer data es comprova a l'enviar el request
	datasize = MSS
	while datasize == MSS:
		codi = clientSocket.recv(MSS+4)
		tupla = (unpack('bbH', codi[0:4]))
		if(tupla[1] != 3):	# Si missatge d'error:
			print('El servidor ha retornat un error. Missatge d error: ')
			miss_error = codi[2:].decode()
			print(miss_error)
			quit()
		s_seq = tupla[2]
		if(s_seq == nextseq%MODULSEQ):	# Si el numero de sequencia coincideix amb l'esperat, enviem ACK
			print('paquet amb nseq '+str(s_seq)+' rebut')
			datasize=len(codi[4:])
			fitxer.write(codi[4:])
			nextseq = (nextseq + 1)%MODULSEQ
			ack = pack('bbH', 0, 4, s_seq)
			clientSocket.sendto(ack, (serverName,serverPort))
			paquets_rebuts = paquets_rebuts + 1
		else:					# Si no, enviem ACK de paquet anterior.
			print('error, esperaba nseq = '+str(nextseq)+' i he rebut un nseq de '+str(s_seq))
			ack = pack('bbH', 0, 4, nextseq-1)
			clientSocket.sendto(ack, (serverName,serverPort))
	print('Fi de la transimissio: ' + str(paquets_rebuts-1) + ' paquets rebuts de ' + str(MSS) + ' bytes i un paquet de '+ str(datasize)+ ', sumant un total de ' + str(datasize+MSS*(paquets_rebuts-1)) + ' bytes.')
	fitxer.close()
	
################### WRQ #######################
elif (tipusTrans == 2):
	fitxer = open("fitxers/"+nom_fitxer,"rb")
	ns = 1
	data=fitxer.read(MSS)
	lastsent=1
	print("Fitxer en proces d'enviarse...")
	clientSocket.sendto(pack('bbH', 0, 3, ns%MODULSEQ%MODULSEQ) +data, (serverName,serverPort))
	print('Paquet amb ns '+str(ns)+' enviat')
	while len(data)==MSS:
		try:		# Mentre encara quedin dades per enviar...
			clientSocket.settimeout(RTO)
			ack = clientSocket.recv(4)
			clientSocket.settimeout(None)
			c_seq = unpack('bbH', ack[0:4])
			if c_seq[1] != 4:
				print('error, capçalera inesperada: '+ str(c_seq[1]))
			if ns%MODULSEQ != c_seq[2]:
				print('error, nseq del ACK no esperat. Esperat: ' + str(ns) + ' Rebut: ' + str(c_seq[2]))
			else:
				data=fitxer.read(MSS)
				paquets_enviats = paquets_enviats + 1
				ns=ns+1 
				clientSocket.sendto(pack('bbH', 0, 3, ns%MODULSEQ%MODULSEQ) +data, (serverName,serverPort))
				print('Paquet amb ns '+str(ns)+' enviat')
		# Si hi ha timeout vol dir que s'ha perdut un paquet, el tornem a enviar.
		except timeout:	
			clientSocket.sendto(pack('bbH', 0, 3, ns%MODULSEQ) +data, (serverName,serverPort))
			print('Paquet amb ns '+str(ns)+' reenviat')
			paquets_perduts = paquets_perduts + 1
			
	while True:
		# Aquest bucle es unicament per enviar l'ultim paquet, que te finalitzacio implicita.
		try:
			clientSocket.settimeout(RTO)
			ack = clientSocket.recv(4)
			clientSocket.settimeout(None)
			c_seq = unpack('bbH', ack[0:4])
			if c_seq[1] != 4:
				print('error, capçalera inesperada: '+ str(c_seq[1]))
			if ns%MODULSEQ != c_seq[2]:
				print('error, nseq del ACK no esperat. Esperat: ' + str(ns) + ' Rebut: ' + str(c_seq[2]))
			else:
				break
		except timeout:
			clientSocket.sendto(pack('bbH', 0, 3, ns%MODULSEQ) +data, (serverName,serverPort))
			print('Paquet amb ns '+str(ns)+' reenviat')
			paquets_perduts = paquets_perduts + 1
			
	print('Fi de la transimissio: ' + str(paquets_enviats) + ' paquets enviats de ' + str(MSS) + ' bytes i un paquet de '+ str(len(data))+ ', sumant un total de ' + str(len(data)+MSS*(paquets_enviats)) + ' bytes.')
	print("S'han hagut de reenviar " + str(paquets_perduts) + " paquets, deixant un total de " + str(paquets_perduts*MSS) + " bytes reenviats.\n")
	fitxer.close()
