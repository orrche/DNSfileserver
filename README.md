DNSfileserver
=============

Silly project, sending a file through the DNS protoco.

All files under the public folder will be transmitted if asked for. They are served in chunks of 500 bytes with the dnspostfix at the end

a.readme_txt.<dnspostfix>

will get the 10th chunk (0x0a) of the readme.txt file _ will be replaced with .


Still havent figured out a real use of this system, if anyone can come up with one dont hessitate to inform me.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/orrche/dnsfileserver/trend.png)](https://bitdeli.com/free "Bitdeli Badge")
