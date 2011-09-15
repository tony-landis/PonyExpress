"""Command-line tool to sync up the couchdb views

Usage::

		$ python -m ponyexpress.couch_sync

"""

import sys
import manage

if __name__ == '__main__':
	outfile = sys.stdout
	outfile.write(manage.couch_sync())
