# -*- encoding:utf-8 -*-

from flask import Flask
import os
import couch
import core

from couchdbkit.loaders import FileSystemDocsLoader


app = Flask(__name__)
app.config.from_envvar('PONYEXPRESS_CFG')

def couch_sync():
	couch_db = couch.init(app.config)
	path = os.getcwd()  
	path = path.replace('/manage.py','')
	if not path:
		return "You must provide the path to PonyExpress"
	dir = '%s/ponyexpress/_design' % path
	print "Syncronizing Couchdb Views from %s" % dir
	loader = FileSystemDocsLoader(dir)
	loader.sync(couch_db, verbose=True)

def queue():
	print ""
	print "Connecting to Couchdb..."
	couch.init(app.config)
	i = 0
	for doc in couch.PonyExpressMessage.by_status(status='queued', limit=250).all():
		i += 1
		rs = {}
		try:
			pony = core.PonyExpress.from_couchdb(doc=doc)
			rs = pony.send(config=app.config)
		except Exception, e:
			print "Exception: %s" % e
			'update status to failed'
			doc.status = 'failed'
			doc.save()
		if (rs or {}).get('result'):
			print "Success: %s" % doc._id
		else:
			print "Failed: %s" % doc._id
	print "Finished processing %s messages" % i 
	print ""
	return 'Finished Processing %i messages(s)' % i

def no_date():
	print "updating all without dates to queued"
	i = 0
	couch.init(app.config)
	for doc in couch.PonyExpressMessage.no_date(limit=1200).all():
		if doc.template == 'vp_shared':
			doc.delete()
			continue
		doc.status = 'queued'
		doc.save()
		i += 1
	return 'Finished Processing %i orphans(s)' % i

	

