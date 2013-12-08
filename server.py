import socket
import ConfigParser, os
from string import find


config = ConfigParser.ConfigParser()
config.read(['config.cfg'])


class FileServer:
	def __init__(self):
		self.f = open('workfile', 'r')
	def getData(self, position, l):
		self.f.seek(position, 0)
		return self.f.read(l)
		


class DNSQuery:
	def __init__(self, data, fileServer):
		self.data=data
		self.domain=''
		self.fileServer = fileServer
		
		tipo = (ord(data[2]) >> 3) & 15   # Opcode bits
		if tipo == 0:                     # Standard query
			ini=12
			lon=ord(data[ini])
			while lon != 0:
				self.domain+=data[ini+1:ini+lon+1]+'.'
				ini+=lon+1
				lon=ord(data[ini])

	def response(self):
		packet=''
		if self.domain:
			domainData = self.domain.split(".")

			chunkNr = -1;
			try:
				chunkNr = int(domainData[0],16)
			except ValueError:
				return False;

			# prepearing the dns header
			packet+=self.data[:2] + "\x81\x80"
			packet+=self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'
			packet+=self.data[12:12 + 5 + len(self.domain)]
			packet += '\xc0\x0c'
			packet += '\x00\x10\x00\x01\x00\x00\x3c\x3c'
			
			data = fileServer.getData(chunkNr * 500 ,500)

			# Calculate number of chunks
			chunks = int(len(data)/256) + 1
			
			size = len(data) + chunks 
			packet += chr((size & 0xFF00)>>8) + chr(size & 0x00FF)

			for x in range(chunks + 1):
				dataChunk = data[x*255:x*255+255]
				packet += chr(len(dataChunk)) + dataChunk 
		return packet

if __name__ == '__main__':
	fileServer = FileServer()
  
	udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	bindAddr = config.get('server', 'bind')
	udps.bind((bindAddr,53))
  
	try:
		while 1:
			data, addr = udps.recvfrom(1024)
			p=DNSQuery(data, fileServer)
			response = p.response()
			if ( response != False ): 
				udps.sendto(response[0:-1], addr)
				print 'TXT chunk for - to: %s -> %s' % (p.domain[0:-1], addr[0])
	except KeyboardInterrupt:
		print 'Terminated'
		udps.close()
