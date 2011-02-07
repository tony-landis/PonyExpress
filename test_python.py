
from ponyexpress.core import PonyExpress
pony = PonyExpress(
	id='test', # The template doc._id
	sender_name = 'The Widget Team',
	sender_address = 'sales@widgets.com',
	recipient_name = 'John Doe',
	recipient_address = 'tony.landis@gmail.com',
	lang = 'es',
	replacements = dict(name='John', new_balance="$25", purchase='5 Widgets'),
	tags = ['newbalance','someothertag']
)
"""
if your couchdb does not use the defaults of 127.0.0.1:5984, database 'ponyexpress'
then you will need to pass that with the to_couchdb() call. Otherwise do not pass
a config value.
"""
config = {'COUCH_CONN':'http://127.0.0.1:5984', 'COUCH_DB':'ponyexpress'}
doc = pony.to_couchdb(config=config)
print doc._id



from ponyexpress.core import PonyExpress
pony = PonyExpress(
	id='test', # The template doc._id
	sender_name = 'The Widget Team',
	sender_address = 'sales@widgets.com',
	recipient_name = 'John Doe',
	recipient_address = 'tony.landis@gmail.com',
	lang = 'es',
	replacements = dict(name='John', new_balance=25, purchase='5 Widgets'),
	tags = ['newbalance','someothertag']
)

"""
If your couchdb does not use the defaults of 127.0.0.1:5984, database 'ponyexpress'
then you will need to pass that with the send() call.

Also, if you use something other than localhost:25 for SMTP or need to provide 
SMTP auth, you will need to pass that in the config.

Otherwise do not pass a config value.
"""
config = {'COUCH_CONN':'http://127.0.0.1:5984', 'COUCH_DB':'ponyexpress', 'SMTP_STRING':'host|25|user|pass'}
rs = pony.send(config=config)
print rs

