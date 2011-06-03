# manage.py
# -*- encoding:utf-8 -*-

from flask import Flask
from flaskext.actions import Manager
from ponyexpress import app
from ponyexpress import couch
from ponyexpress import core
from couchdbkit.designer import push
import sys, os

app = Flask(__name__)
app.config.from_envvar('PONYEXPRESS_CFG')
manager = Manager(app)

@manager.register('couch_sync')
def couch_sync(app):
	"""
	Syncronize the locale views to couchdb
	"""
	def action():
		path = os.getcwd()  
		path = path.replace('/manage.py','')
		if not path:
			return "You must provide the path to PonyExpress"
		for sub in ['ponyexpress','stats']:
			dir = '%s/ponyexpress/_design/%s' % (path,sub)
			print "Syncronizing Couchdb Views from "
			print dir
			print ""
			couch_db = couch.init(app.config)
			push(dir, couch_db)
	return action


@manager.register('queue')
def queue(app):
	"""
	Send all messages in a status of "queued"
	"""
	def action():
		print ""
		print "Connecting to Couchdb..."
		couch_db = couch.init(app.config)
		i = 0
		for doc in couch.PonyExpressMessage.by_status(status='queued', limit=250).all():
			i += 1
			rs = {}
			try:
				pony = core.PonyExpress.from_couchdb(doc=doc)
				rs = pony.send(config=app.config)
			except Exception, e:
				print "Exception: %s" % e
			if (rs or {}).get('result'):
				print "Success: %s" % doc._id
			else:
				print "Failed: %s" % doc._id
		print "Finished processing %s messages" % i 
		print ""
	return action


if __name__ == "__main__":
	manager.run()
