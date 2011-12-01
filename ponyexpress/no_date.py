"""Command-line tool to fix the ponyexpress qeueue for failed stuff

Usage::

		$ python -m ponyexpress.no_date

"""

import sys
import manage

if __name__ == '__main__':
	outfile = sys.stdout
	outfile.write(manage.no_date())
