from flask import Flask, session, redirect, url_for, request, render_template, jsonify
import core
import couch
import formencode
import gearman

class TemplateForm(formencode.Schema):
	"""
	Formencode Form validators for Email Template add/edit
	"""
	allow_extra_fields = True
	filter_exter_fields = True
	pre_validators = [formencode.variabledecode.NestedVariables()]
	_id = formencode.validators.String(not_empty=True, if_missing=None)
	name = formencode.validators.String(not_empty=True)
	class contents(formencode.Schema):
		lang = formencode.validators.String(not_empty=False)
		subject = formencode.validators.String(not_empty=False)
		body = formencode.validators.String(not_empty=False)
	contents = formencode.ForEach(contents)

app = Flask(__name__)

try:
	app.config.from_envvar('PONYEXPRESS_CFG')
except Exception, e:
	print e
	app.config.update(
		DEBUG=True,
		GEARMAN_SERVERS='localhost:4730',
		SMTP_STRING='localhost|25',
		COUCHDB_CONN='127.0.0.1:',
		COUCH_CONN = 'http://127.0.0.1:5984',
		COUCH_DB = 'ponyexpress'
	)

@app.route('/')
def index():
	'get some gearman stats'
	gmc = gearman.GearmanAdminClient([app.config.get('GEARMAN_SERVER','localhost:4730')])
	gm_status, gm_version, gm_workers, gm_ping = 'NA', '', [], 0
	try:
		gm_status = gmc.get_status()
		gm_version = gmc.get_version()
		gm_workers = gmc.get_workers()
		gm_ping = gmc.ping_server()
	except Exception:
		pass
	return render_template('index.html', 
		session=session,
		gm_status=gm_status, gm_version=gm_version, gm_workers=gm_workers, gm_ping=gm_ping)

@app.route('/add_template')
def add_template():
	return render_template('add.html')

@app.route('/create_template', methods=['POST'])
def create_template():
	"save a new template"
	try:
		form = TemplateForm.to_python(request.form)
	except formencode.validators.Invalid, error:
		return str(error)
	else:
		lc = couch.LocalTemplate(
		lang=form.get('lang'),
		subject=form.get('subject'),
		body=form.get('body')
		)
		doc = couch.PonyExpressTemplate(
		_id = form.get('_id'),
		name=form.get('name'),
		format=form.get('format'),
		contents = [lc]
		)
		doc.save()
		return redirect(url_for('view_template', doc_id=doc._id))

@app.route('/delete_template/<doc_id>')
def delete_template(doc_id):
	doc = couch.PonyExpressTemplate.get(doc_id)
	doc.delete()
	return redirect(url_for('list_templates'))

@app.route('/template/<doc_id>')
def view_template(doc_id):
	doc = couch.PonyExpressTemplate.get(doc_id)
	doc.contents.append(couch.LocalTemplate(lang='NEW',subject='',body=''))
	contents = enumerate(doc.contents)
	return render_template('view_template.html', doc=doc, contents=contents)

@app.route('/save_template/<doc_id>', methods=['POST'])
def save_template(doc_id):
	doc = couch.PonyExpressTemplate.get(doc_id)
	try:
		form = TemplateForm.to_python(request.form)
	except formencode.validators.Invalid, error:
		return str(error)
	else:
		doc.contents = []
		for k,v in form.iteritems():
			if not k == 'contents':
				setattr(doc, k, v)
			elif k == 'contents':
				for content in v:
					if all([content.get(key, None) for key in ('lang','subject','body')]):
						doc.contents.append(couch.LocalTemplate(**content))
		doc.save()
		return redirect(url_for('view_template', doc_id=doc._id))
					
@app.route('/list_templates')
def list_templates():
	view = couch.PonyExpressTemplate.view('ponyexpress/all_templates')
	return render_template('list_templates.html',
		results=view.all())

@app.route('/send', methods=['PUT'])
def send():
	"""
	RESTfull inteface to send messages
	"""
	if request.method == 'PUT':
		'JSON expected'	
		pony = core.PonyExpress.from_dict(request.json)
		rs = pony.send(config=app.config)
		return jsonify(rs)

def run_queue():
	"""
	Send all messages in a status of "queued"
	"""
	rs = []
	for doc in rs:
		pony = core.PonyExpress.from_couchdb(doc=doc)
		rs = pony.send(config=app.config)
		if (rs or {}).get('result'):
			print "Success: %s" % doc._id
		else:
			print "Failed: %s" % doc._id
	return "Finished processing %s" % len(rs)


if __name__ == '__main__':
	# couchdb init
	couch_db = couch.init(app.config)
	# TODO - make this part of setup/install ?
	from couchdbkit.designer import push
	push('/Users/tony/git/PonyExpress/ponyexpress/_design/ponyexpress', couch_db)
	# TODO - make the settings below CLI options
	app.run(host='0.0.0.0', port=4000)
