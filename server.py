import socket
import ConfigParser, os
from string import find


config = ConfigParser.ConfigParser()
config.read(['config.cfg'])

class DNSQuery:
	def __init__(self, data, dnspostfix):
		self.data=data
		self.domain=''
		self.dnspostfix = dnspostfix
		self.dnspostfixlen = len(dnspostfix)

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
			fileData = self.domain[0: -(self.dnspostfixlen+2)]

			domainData = fileData.split(".")

			filepath = os.path.join('public', '/'.join(domainData[1:]))
			f = open(filepath, 'r')

			print domainData

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
			
			f.seek(chunkNr*500)
			data = f.read(500)

			# Calculate number of chunks
			chunks = int(len(data)/256) + 1
			
			size = len(data) + chunks 
			packet += chr((size & 0xFF00)>>8) + chr(size & 0x00FF)

			for x in range(chunks + 1):
				dataChunk = data[x*255:x*255+255]
				packet += chr(len(dataChunk)) + dataChunk 
		return packet

if __name__ == '__main__':
	udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	bindAddr = config.get('server', 'bind')
	udps.bind((bindAddr,53))
  
	try:
		while 1:
			data, addr = udps.recvfrom(1024)
			p=DNSQuery(data, config.get('server', 'dnspostfix'))
			response = p.response()
			if ( response != False ): 
				udps.sendto(response[0:-1], addr)
				print 'TXT chunk for - to: %s -> %s' % (p.domain[0:-1], addr[0])
	except KeyboardInterrupt:
		print 'Terminated'
		udps.close()
