"""
Core PonyExpress Class
"""

import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import couch
import json

class PonyExpressException(Exception):
	"""
	Handle exceptions, log the error and
	message to couchdb so it can be reported
	and resent later
	"""
	def __init__(self, pony, type, error):
		log = couch.PonyExpressError(
			date = datetime.datetime.now(),
			type = type,
			exception = str(error),
			template_id = pony._id,
			pony_json = pony.to_dict()
		)
		log.save()

class PonyExpress(object):
	'fallback language to use when the requested language is unavailable'
	_lang = 'en'
	'parties'
	_sender_name = 'nobody'
	_sender_address = 'nobody@localhost'
	_recipient_name = None
	_recipient_address = None
	'smpt connection'
	_smpt_connection = None
	'recipients'
	_recipients = None
	'smtp connection'
	_smtp_connection = None
	'the couch template doc'
	_id = None
	_template = None
	'the tags for the message log'
	_tags = None
	'the dict of replacements for the template'
	_replacements = None
	'the couchdb message doc'
	_message_doc = None
	
	def __init__(self, id, recipient_name=None, recipient_address=None, sender_name=None, sender_address=None, tags=None, replacements=None, **kwargs):
		"get the template"
		self._id = id
		self._recipient_name = recipient_name
		self._recipient_address = recipient_address
		assert self._id, "No Template ID Passed"
		assert self._recipient_address, "No Recipient Address Passed"
		assert self._recipient_name, "No Recipient Name Passed"
		self._sender_name = sender_name or self._sender_name
		self._sender_address = sender_address or self._sender_address
		self._tags = tags or []
		self._replacements = replacements or {}

	def to_json(self):
		"""
		Encode the JSON dict to be passed around
		"""
		return json.dumps(self.to_dict())
	
	@classmethod
	def from_json(cls, encoded_json, **kwargs):
		"""
		Setup a PonyExpress object usting encoded JSON 
		"""
		decoded_json = json.loads(encoded_json)
		return cls.from_dict(decoded_json, **kwargs)

	def to_dict(self):
		"""
		Encode the JSON dict to be passed around
		"""
		params = dict(id=self._id, recipient_name=self._recipient_name, recipient_address=self._recipient_address)
		if self._sender_name: params.update(sender_name=self._sender_name)
		if self._sender_address: params.update(sender_address=self._sender_address)
		if self._tags: params.update(tags=self._tags)
		if self._replacements: params.update(replacements=self._replacements)
		return params

	@classmethod
	def from_dict(cls, decoded_json, **kwargs):
		"""
		Setup a PonyExpress object using a dict of values
		"""
		dict = {}
		# hack to fix older python versions (<2.7?) that dont allow unicode keywords
		for k,v in decoded_json.iteritems(): dict[str(k)] = v
		return cls(**dict)
	
	def to_couchdb(self, status='queued', save=True, config=None):
		"""
		Create a PonyExpressMessage document for couchdb logging or queue.
		"""
		self._message_doc = couch.PonyExpressMessage(
			status = status,
			date = datetime.datetime.now(),
			template = self._id,
			lang = self._lang,
			sender_address = self._sender_address,
			recipient_address = self._recipient_address,
			sender_name = self._sender_name,
			recipient_name = self._recipient_name,
			replacements = self._replacements,
			tags = self._tags or [])
		if save:
			# couchdb initialized?
			if not couch.couch_db:
				config = config or {}
				couch.init(config)
			self._message_doc.save()
		return self._message_doc
	
	@classmethod
	def from_couchdb(cls, doc_id=None, doc=None):
		"""
		Setup a PonyExpress object using a queued or failed PonyExpressMessage couchdb doc
		"""
		if not doc:
			doc = couch.PonyExpressMessage(doc_id)
		pony = PonyExpress(id=doc.template,
			sender_address=doc.sender_address,
			sender_name=doc.sender_name,
			recipient_name = doc.recipient_name,
			recipient_address = doc.recipient_address,
			tags = doc.tags,
			replacements = doc.replacements)
		pony._message_doc = doc
		return pony

	def smtp_connect(self, connection):
		"""
		Setup the SMTP connection to use to send this message

		connection:
			either a smtplib.SMTP() connection object
			or pass string with this format: "host|port|user|pass"

		Example use for passing in an existing connection of type smtplib.SMTP:
			>>> # create the connection
			>>> connection = smtplib.SMTP('mail.gmail.com', port=25)
			>>> # login with our SMPT user/pass
			>>> connection.login('username', 'password')
			>>> # pass it into the MailTpl() object
			>>> smtp_connect(connection) 
		
		Example use for passing in a string:
			>>> # connection string with no login info
			>>> smtp_connect('mail.gmail.com|25')
			>>> # connection string with login info
			>>> smtp_connect('mail.gmail.com|25|user|pass')
		"""
		if not isinstance(connection, smtplib.SMTP):
			'You gave me a connection string, I will try and connect.'
			conn_parts = str(connection).split("|")
			conn_len = len(conn_parts)
			'determine the host'
			conn_host = str('localhost' if not conn_len > 0 else conn_parts[0])
			'determine the port'
			conn_port = int(25 if not conn_len > 1 else conn_parts[1])
			'determine the user'
			conn_user = str('' if not conn_len > 2 else conn_parts[2])
			'determine the pass'
			conn_pass = str('' if not conn_len > 3 else conn_parts[3])
			'create the connection'
			connection = smtplib.SMTP(conn_host, conn_port)
			if len(conn_user):
				'authenticate if user was passed in the connection string'
				connection.login(conn_user, conn_pass)
		'ready for use'
		self._smtp_connection = connection
		return self._smtp_connection

	def compile(self, lc):
		"""
		Gets the values for replacement and performs string replacement
		"""
		subject, body = lc.subject, lc.body
		htm_body, txt_body = None, None
		if self._replacements:
			'value replacement is possible, we have a dict of replacement values'
			# convert all keywords to strings for safe_substitute()
			kwds = {}
			for k,v in self._replacements.iteritems(): kwds[str(k)]=v	
			# perform substitutions
			subject = unicode(Template(subject).safe_substitute(**kwds))
			body = unicode(Template(body).safe_substitute(**kwds))

		if self._template.format == 'text':
			txt_body = body
		elif self._template.format == 'html':
			htm_body = body
		return subject, htm_body, txt_body

	def send(self, config=None):
		"""
		Send the current message.

			* Make sure we have a valid smtp connection
			* Connect to couchdb and get the template
			* Get the language specific subject/body from couchdb
			* Render the subject/body, with variable replacement
			* Send the message

		If sending fails at any stage of the way, we will
		log the exception and current message details to
		couch so we can retry.
		"""

		# open an STMP connection if not done already
		if not self._smtp_connection:
			try:
				self.smtp_connect((config or {}).get('SMTP_STRING', None))
			except Exception, e:
				raise PonyExpressException(self, "SMTP", str(e))
				return dict(status=False, id=None, error="SMTP: %s" % str(e))

		# init couch if not done alread
		if not couch.couch_db: couch.init(config=config)

		# load the template
		try:
			self._template = couch.PonyExpressTemplate.get(self._id)
		except Exception, e:
			raise PonyExpressException(self, "COUCH", str(e))
			return dict(status=False, id=None, error="COUCH: %s" % str(e))
		
		lc_try = [lc for lc in self._template.contents if lc.lang == self._lang]
		if lc_try:
			'lang match'
			lc = lc_try[0]
		elif self._lang != self._fallback_language:
			'no lang match, use fallback'
			lc_try = [(lc) for lc in self._template.contents if lc.lang == self._fallback_language]
			if lc_try:
				lc = lc_try[0]
			else:
				'no localized template exist for the fallback lang'
				e = 'Unable to load language selected (%s)' % self._fallback_language
				raise PonyExpressException(self, "LOCALE", str(e))
				return dict(status=False, id=None, error="LOCALE: %s" % str(e))

		'variable replacement and markdown'
		subject, html_body, text_body = self.compile(lc)

		'setup the msg object'
		if html_body and text_body:
			format = 'both'
			msg = MIMEMultipart('alternative')
			msg.attach(MIMEText(text_body, 'plain'))
			msg.attach(MIMEText(html_body, 'html'))
		elif html_body:
			format = 'html'
			msg = MIMEText(html_body.encode('utf-8', 'replace'), 'html', 'utf-8')
		elif text_body:
			format = 'text'
			msg = MIMEText(text_body.encode('utf-8', 'replace'), 'plain', 'utf-8')

		msg['Subject'] = subject
		msg['Return-Path'] = self._sender_address
		msg['From'] = "%s <%s>" % (self._sender_name, self._sender_address)
		msg['To'] = self._recipient_address

		try:
			'try sending the message via SMTP'
			self._smtp_connection.sendmail(msg['From'], self._recipient_address, msg.as_string())
			'success, log the message to couchdb'
			if not self._message_doc:
				self._message_doc = self.to_couchdb(status='sent', save=False)
			self._message_doc.date = datetime.datetime.now()
			self._message_doc.status = 'sent'
			self._message_doc.subject = subject
			self._message_doc.body = text_body or html_body
			self._message_doc.save()
			return dict(result=True, id=self._message_doc._id)
		except Exception, e:
			'if doc is open, update status to failed'
			if self._message_doc:
				self._message_doc.status = 'failed'
				self._message_doc.save()
			'log the error to couchdb'
			raise PonyExpressException(self, "SEND", str(e))
			return dict(result=False, id=None, error="SEND: %s" % str(e))
