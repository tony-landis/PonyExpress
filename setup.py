from distutils.core import setup

setup(
    name='PonyExpress',
    version='0.15stable',
		author = 'Tony Landis',
		author_email = 'tony.landis@gmail.com',
    packages=['ponyexpress',],
		url = 'https://github.com/tony-landis/PonyExpress',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
	description="""
		High performance, transactional email message queuing, logging,\
		and multi-lingual HTML and plain text templates management.
		""",
    long_description=open('README.md').read(),
		install_requires=[
			'Flask',
			'Flask-Actions',
			'formencode',
			'couchdbkit',
			'gearman',
		]
)
