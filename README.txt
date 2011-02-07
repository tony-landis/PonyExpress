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

	export PONYEXPRESS_CFG=/FULL PATH TO/settings.cfg

Or on windows:

	set PONYEXPRESS_CFG=\FULL PATH TO\settings.cfg

Edit settings.cfg and set the SMTP string to a valid host and port:

	SMTP_STRING = "mail.server.com|25"

If SMTP authentication is required, then set the SMTP_STRING like this:

	SMTP_STRING = "mail.server.com|25|user|password"


Starting the PonyExpress Server
-------------------------------

You can now startup the PonyExpress web server (http://packages.python.org/Flask-Actions/)

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

For the example above, we just used the free couchone database I set up for demonstration purpose.

You will need to open settings.cfg again and update COUCH_CONN to your own couch database now.

To add the couchdb views required for the reports and lists, run this:

	manage.py couch_sync

You can then restart the PonyExpress


