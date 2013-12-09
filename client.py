import ConfigParser, os

import dns.resolver
import dns.message
import dns.query
import dns.flags

import sys


config = ConfigParser.ConfigParser()
config.read(['config.cfg'])

chunk = 0

while True:
	domain = hex(chunk)[2:] + '.' + sys.argv[1]

	resolver = dns.resolver.Resolver()
	resolver.nameservers = [config.get('client', 'nameserver')]

	answers = resolver.query(domain, dns.rdatatype.TXT)

	if ( len(answers) < 1 ):
		break;
	for rdata in answers:
		if ( len(rdata.strings) == 0 or rdata.strings[0] == '' ):
			sys.exit(1); 
		for s in rdata.strings:
			sys.stdout.write(s)
	chunk+=1
