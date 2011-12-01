"""
The couchdbkit document models
"""

from couchdbkit import *

couch_db = None

def init(config, couch_db=couch_db):
	server = Server(config.get('COUCH_CONN', 'http://127.0.0.1:5984'))
	couch_db = server.get_or_create_db(config.get('COUCH_DB', 'ponyexpress'))
	PonyExpressTemplate.set_db(couch_db)
	PonyExpressError.set_db(couch_db)
	PonyExpressMessage.set_db(couch_db)
	return couch_db

class LocalTemplate(DocumentSchema):
	"""
	Dict Schema for localized template content
	"""
	lang = StringProperty() # US, EN, etc
	subject = StringProperty()
	body = StringProperty()

class PonyExpressTemplate(Document):
	"""
	Couchdbkit document model for message template
	"""
	name = StringProperty()
	format = StringProperty() # (text|html)
	contents = SchemaListProperty(LocalTemplate)

class PonyExpressError(Document):
	"""
	For logging exceptions
	"""
	date = DateTimeProperty()
	type = StringProperty()
	exception = StringProperty()
	template_id = StringProperty()
	pony_json = DictProperty()

class PonyExpressMessage(Document):
	"""
	Full log of sent|queued messages
	"""
	date = DateTimeProperty()
	status = StringProperty() 	# sent, queued, failed
	template = StringProperty() # the PonyExpressTemplate._id
	lang = StringProperty()
	format = StringProperty()
	sender_address = StringProperty()
	recipient_address = StringProperty()
	sender_name = StringProperty()
	recipient_name = StringProperty()
	tags = ListProperty()
	replacements = DictProperty()
	subject = StringProperty()
	body = StringProperty()

	@classmethod
	def by_status(cls, status, **kwargs):
		"view by status (queued, sent, failed)"
		return cls.view('ponyexpress/messages_by_status', key=status, **kwargs)
	
	@classmethod
	def no_date(cls, **kwargs):
		"view all with no date"
		return cls.view('ponyexpress/messages_no_date', **kwargs)
	
