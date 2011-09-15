# manage.py
# 
# Some CLI Tools
#
# -*- encoding:utf-8 -*-

from flask import Flask
from flaskext.actions import Manager
import ponyexpress.manage

app = Flask(__name__)
app.config.from_envvar('PONYEXPRESS_CFG')
manager = Manager(app)

@manager.register('couch_sync')
def couch_sync(app):
	"""
	Syncronize the locale views to couchdb
	"""
	return ponyexpress.manage.couch_sync

@manager.register('queue')
def queue(app):
	"""
	Send all messages in a status of "queued"
	"""
	return ponyexpress.manage.queue

if __name__ == "__main__":
	manager.run()
