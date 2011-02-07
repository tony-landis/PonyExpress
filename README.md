PonyExpress
===========

High performance, transactional email message queuing, logging, 
and multi-lingual HTML and plain text templates management.

PonyExpress offers great flexibility so that it can be used by non-python applications:

* Send JSON to the REST interface (language and platform agnostic)
* Create a Couchdb document (language and platform agnostic)
* Send JSON to a Gearman job (gearman libraries exist for numerous languages)
* Use the PonyExpress class (python) 

Managing Email Copy and Translations
------------------------------------

Hardcoding email copy into application code is very messy, and does not provide a mechanism
for non-developers to make changes to the copy or for translators to do their work. 

PonyExpress provides a web interface to free programmers from the mess of maintaining email
copy in their code base. It also allows an extremely simple mechanism for sending an email
from anywhere in the application, complete with variable replacement, and custom tags for reporting.


Queues, Performance, Scalability, and Load Balancing
----------------------------------------------------

For high performance applications, waiting for an SMTP connection and response is a big performance hit.

PonyExpress enables applications to distribute email processing load by providing a queue that messages
can be pushed to asynchronously.

Messages can be queued to Couchdb, which has has excellent replication capabilities.

Also, PonyExpress offers a Gearman interface, which is higher performance and also uses
Couchdb for logging the messages and any errors.

The simplest approach to get up and running with PonyExpress is to use the Couchdb
queue method. It is also the most fault tolerant, as Couchdb is the only service that
needs to be running in order for the queue insertion.

Only applications that need to be able to hand off an email to the queue in a few milliseconds
or less would see an advantage to implementing Gearman, as the trade off for that quick transaction
is the requirement that a Gearman server and the worker daemon to be up and running, 
in addition to Couchdb which is still used for message and error logging.


Error Handling
--------------

When PonyExpress cannot send a message, for example, because the SMTP service is down or times out,
it creates a log in Couchdb with the error and the details needed to resend the message.

This frees developers from creating their own email failure routines, as
well as providing a simple way to see what messages have failed and for what reason.


Message Logging
---------------

PonyExpress logs all emails sent, and provides reports that free developers from writing more
reports and logging the data themselves. Custom tags can be passed into each message sent, and
used in reporting later.


Language and Platform Independent
---------------------------------

The ability add a message to the queue simply by creating a Couchdb document is a great way
to get all the features of PonyExpress regardless of the language being used, or the platform
being developed on.



Getting Started with PonyExpress
================================

To get started, clone the git repo and run setup.py

	git clone git@github.com:tony-landis/PonyExpress.git
	cd PonyExpress
	python setup.py install
	cp default_settings.cfg settings.cfg

On linux/unix:

	export PONYEXPRESS_CFG=`pwd`/settings.cfg

Or on windows:

	set PONYEXPRESS_CFG=\FULL PATH TO\settings.cfg

Edit settings.cfg and set the SMTP string to a valid host and port:

	SMTP_STRING = "mail.server.com|25"

If SMTP authentication is required, then set the SMTP_STRING like this:

	SMTP_STRING = "mail.server.com|25|user|password"


Starting the PonyExpress Server
-------------------------------

You can now startup the PonyExpress web server (http://packages.python.org/Flask-Actions/)

	export PONYEXPRESS_CFG=`pwd`/settings.cfg
	python ponyexpress/__init__.py

You should see:

 * Running on http://0.0.0.0:4000/
 * Restarting with reloader...

You can now go to http://127.0.0.1:4000/ with your web browser. Here you can manage
email templates and view reports. If you are running a gearman server, the ping time,
jobs, and workers will be summarized there.


Sending Your First Email
------------------------

Here is an example to send an email via the REST API for immediate delivery:

curl -X PUT http://localhost:4000/send \
	-H "Content-Type: application/json" \
	-d '{"id":"test", "replacements":{"name":"Your Name", "from":"Pony Express", "sig":"This is my signature\nLine of Signature"}, "tags":["pony","express"], "recipient_name":"Your Name", "recipient_address":"you@you.com", "sender_name":"Pony Express", "sender_address":"you@you.com"}'

If all went well, we should see a response similar to this, where id is the couchdb doc._id of the message log.

	{
 	 "id": "1cbb1b9400396a1b7cb0e7b35b1eecd4", 
 	 "result": true
	}

You can view the message doc here:

	http://ponyexpress.couchone.com/ponyexpress/1cbb1b9400396a1b7cb0e7b35b1eecd4


Configuring Couchdb
-------------------

The example above used the free couchone database I set up for demonstration purpose.

You will need to open settings.cfg again and update COUCH_CONN to your own couch database now.

To add the couchdb views required for the reports and lists, run this:

	export PONYEXPRESS_CFG=`pwd`/settings.cfg
	python manage.py couch_sync

You can then restart the PonyExpress server and add your own e-mail templates.


Managing Email Templates
------------------------

With the PonyExpress Server running, you can vist http://127.0.0.1:4000/add_template to add an email template.

	Tag: This is the id that you will pass later when actually sending an email
	Name: A name to help you remember the function of the template later
	Content Type: If you are entering HTML into the body, select HTML, otherwise select Plain Text
	Default Language: The default language for this template. en, es, etc...
	Subject: The subject line for the email
	Body: The full email body

After saving the template, you will be giving the opportunity to add translations for other languages.

You can use replacements in the Subject and Body, and any keys passed in the replacements dictionary
when sending a message will be replaced with the values.

For example:

	Template Body: 
	--------------
	Hello $name,
	Your balance is now $new_balance after your purchase of $purchase.
	Thank you,
	$sig


	Replacement Dict:
	-----------------
	{ 
		'name': 'John',
		'new_balance': '$25',
		'puchase': '5 Widgets',
		'sig': 'The Widget Team\n1-800-222-3333'
	}


	Rendered Body:
	--------------
	Hello John,
	Your balance is now $25 after your purchase of 5 Widgets.
	Thank you,
	The Widget Team
	1-800-222-3333'


Adding Messages to the Couchdb Queue (python method)
----------------------------------------------------

The simplest method to start queuing messages is with the python library.

Here is an example, this message will be stored in couchdb for later processing.

	from ponyexpress.core import PonyExpress
	pony = PonyExpress(
		id='test', # The template doc._id
		sender_name = 'The Widget Team',
		sender_address = 'sales@widgets.com',
		recipient_name = 'John Doe',
		recipient_address = 'john@gmail.com',
		lang = 'es',
		replacements = dict(name='John', new_balance=25, purchase='5 Widgets'),
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


Adding Messages to the Couchdb Queue (non-python method)
--------------------------------------------------------

You can achieve the same result as above without using the python library.

Just put the a document in your couchdb using this structure:

	curl -X POST http://127.0.0.1:5984/ponyexpress/ \
		-H "Content-Type: application/json" \
		-d '{"doc_type": "PonyExpressMessage", 
	   		"template": "test", 
  	 		"status": "queued", 
				"sender_name": "The Widget Team",
				"sender_address": "sales@widgets.com", 
				"recipient_name": "John Doe", 
				"recipient_address": "john@gmail.com", 
				"lang": "en", 
				"replacements": { "name":"John", "new_balance":"$25", "purchase":"5 Widgets" }, 
				"tags":["newbalance", "someothertag"]}'


Processing the Couchdb Queue
----------------------------

After adding emails into the queue using one of the couchdb methods below, 
the next step is to process the queue. To do so, simply run the following command:

	export PONYEXPRESS_CFG=`pwd`/settings.cfg
	python manage.py queue

You should see something like this:

	Connecting to Couchdb...
	Success: 1bc02b88ef8125a9ea72f1c54692bab9
	Finished processing 1 messages


Sending Messages without Queueing (python method)
-------------------------------------------------

If you want to send a message withough putting it in a queue,
you must use the python library:

	from ponyexpress.core import PonyExpress
	pony = PonyExpress(
		id='test', # The template doc._id
		sender_name = 'The Widget Team',
		sender_address = 'sales@widgets.com',
		recipient_name = 'John Doe',
		recipient_address = 'john@gmail.com',
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
	config = {'COUCH_CONN':'http://127.0.0.1:5984', 'COUCH_DB':'ponyexpress', 'SMTP_STRING':'mail.some.com|25|user|pass'}
	rs = pony.send(config=config)
	print rs



Using Gearman for High Performance 
----------------------------------

To utilize gearman for high performance messaging, you must first start 
the python worker script for gearman. This assumes you have already configured
the correct gearman ip:port in settings.cfg and have a gearmand service running
at that ip:port.

	export PONYEXPRESS_CFG=`pwd`/settings.cfg
	python run_gearman.py

You can now hand off jobs to gearman, here is an example for Python:
	
	from ponyexpress.gearman_interface import PonyExpressClient
	pony = PonyExpressClient(
		id='test', # The template doc._id
		sender_name = 'The Widget Team',
		sender_address = 'sales@widgets.com',
		recipient_name = 'John Doe',
		recipient_address = 'john@gmail.com',
		lang = 'es',
		replacements = dict(name='John', new_balance=25, purchase='5 Widgets'),
		tags = ['newbalance','someothertag']
	)

	# send in background, non blocking
	rs = pony.to_gearman(['localhost:4730'], background=True, wait_until_complete=False)
	print "Status: %s" % rs.get('result')
	print "Doc Id: %s" % rs.get('id')

	# send and wait for response
	rs = pony.to_gearman(['localhost:4730'])
	print "Status: %s" % rs.get('result')
	print "Doc Id: %s" % rs.get('id')
