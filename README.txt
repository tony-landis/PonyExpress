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

# easy_install PonyExpress


