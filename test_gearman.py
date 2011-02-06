# test_gearman.py
# -*- encoding:utf-8 -*-

c = {
	"id":"test", 
	"recipient_name": 'Tony Landis',
	"recipient_address": 'tony.landis@gmail.com',
	"replacements":{"key":"value", "foo":"bar"},
	"tags":["pony","express"],
	"sender_name":"XYZ Corp", 
	"sender_address":"sales@xyzcorp.com"}

from ponyexpress.gearman_interface import PonyExpressClient
for i in range(1):
	print i
	pony = PonyExpressClient.from_dict(c)
	rs = pony.to_gearman(['localhost:4730'], background=True, wait_until_complete=False)
	print type(rs)
	print "Status: %s" % rs.get('result')
	print "Doc Id: %s" % rs.get('id')
	print ""

rs = pony.to_gearman(['localhost:4730'])
