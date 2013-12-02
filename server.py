import socket
from string import find

class FileServer:
	def __init__(self):
		self.f = open('workfile', 'r')
		self.data = self.f.read()
	def getData(self, position, l):
		return self.data[position : position + l]
		


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

	def respuesta(self, ip):
		packet=''
		print "::", self.data[12:27]
		if self.domain:
			domainData = self.domain.split(".")


			packet+=self.data[:2] + "\x81\x80"
			packet+=self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'   # Questions and Answers Counts
			packet+=self.data[12:12 + 5 + len(self.domain)]                                         # Original Domain Name Question
			print 12 + 5 + len(self.domain)
			packet += '\xc0\x0c'                                             # Pointer to domain name
			packet += '\x00\x10\x00\x01\x00\x00\x00\x3c'
			
			data = fileServer.getData(int(domainData[0], 16),200)

			packet += '\x00' + chr(len(data)+7)             # Response type, ttl and resource data length -> 4 bytes
			print int(domainData[0], 16)
			packet += chr(len(data)) + data 
			packet += '\x05\x00ejdd'
			packet+=self.data[27:]
		return packet

if __name__ == '__main__':
	fileServer = FileServer()
	ip='192.168.1.1'
	print 'pyminifakeDNS:: dom.query. 60 IN A %s' % ip
  
	udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udps.bind(('127.0.0.1',53))
  
	try:
		while 1:
			data, addr = udps.recvfrom(1024)
			p=DNSQuery(data, fileServer)
			udps.sendto(p.respuesta(ip), addr)
			print 'Respuesta: %s -> %s' % (p.domain, ip)
	except KeyboardInterrupt:
		print 'Finalizando'
		udps.close()
