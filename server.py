#!/usr/bin/env python3
from flask import Flask
from flask import abort
from flask import render_template
from flask import redirect
from flask import request
from flask import session
from flask import url_for

from globals import globals
from help import Help
from events import Events
from index import Index
from inventory import Inventory
from people import People
from robohash import Robohash
from test import Test
from vms import VMs

app = Flask(__name__)
# The handler classes for each route type
help = Help()
events = Events()
index = Index()
inventory = Inventory()
people = People()
robohash = Robohash()
test = Test()
vms = VMs()

config = globals.config

def decode_id(id):
    id = globals.base58_hashids.decode(id)
    if id == None: return None
    if len(id) != 1: return None
    return id[0]

# here all the valid routes are defined, as well as the valid verbs
# for each

# server.py does as little work as considered resonable and hands off
# control to the appropriate handler class.
# usually the hashed id from the url is checked for validitiy first

@app.route('/', methods=['GET'])
def index_():
    if request.method == 'GET':
        return index.index(request, session, events)
    else: abort(405)

@app.route('/help', methods=['GET'])
def help_():
    if request.method == 'GET':
        return help.index(request, session)
    else: abort(405)

@app.route('/login/', methods=['GET', 'POST'])
def people_login():
    if request.method == 'GET':
        return people.login(request, session)
    else:
        return people.login(request, session)

@app.route('/logout', methods=['GET'])
def people_logout():
    if request.method == 'GET':
        return people.logout(request, session)
    else: abort(405)

@app.route('/register/', methods=['GET', 'POST'])
def people_register():
    if request.method == 'GET':
        return people.register(request, session)
    if request.method == 'POST':
        return people.register(request, session)

@app.route('/inventory/', methods=['GET'])
def inventory_():
    if request.method == 'GET':
        return inventory.index(request, session)
    else: abort(405)

@app.route('/inventory/<id>', methods=['GET'])
def inventory_id(id):
    id = decode_id(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return inventory.show(request, session, id)
    else: abort(405)

@app.route('/inventory/<id>/edit', methods=['GET', 'POST'])
def inventory_id_edit(id):
    id = decode_id(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return inventory.edit(request, session, id)
    if request.method == 'POST':
        return inventory.update(request, session, id)
    else: abort(405)

@app.route('/people/', methods=['GET'])
def people_():
    if request.method == 'GET':
        return people.index(request, session)
    else: abort(405)

@app.route('/people/new/', methods=['GET', 'POST'])
def people_new():
    if request.method == 'GET':
        return people.new(request, session)
    elif request.method == 'POST':
        return people.create(request, session)
    else: abort(405)

@app.route('/people/<id>', methods=['GET'])
def people_id(id):
    id = decode_id(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return people.show(request, session, id)
    else: abort(405)

@app.route('/people/<id>/edit', methods=['GET', 'POST'])
def people_id_edit(id):
    id = decode_id(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return people.edit(request, session, id)
    elif request.method == 'POST':
        return people.update(request, session, id)
    else: abort(405)

@app.route('/people/<id>/delete', methods=['GET'])
def people_id_delete(id):
    id = decode_id(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return people.delete(request, session, id)
    else: abort(405)

@app.route('/events/', methods=['GET'])
def events_():
    if request.method == 'GET':
        return events.index(request, session)
    else: abort(405)

@app.route('/events/new/', methods=['GET', 'POST'])
def events_create():
    if request.method == 'GET':
        return events.new(request, session)
    if request.method == 'POST':
        return events.create(request, session)
    else: abort(405)

@app.route('/events/<id>', methods=['GET'])
def events_id(id):
    id = decode_id(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return events.show(request, session, id)
    else: abort(405)

@app.route('/events/<id>/edit', methods=['GET', 'POST'])
def events_id_edit(id):
    id = decode_id(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return events.edit(request, session, id)
    if request.method == 'POST':
        return events.update(request, session, id)
    else: abort(405)

@app.route('/events/<id>/delete', methods=['GET'])
def events_id_delete(id):
    id = decode_id(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return events.delete(request, session, id)
    else: abort(405)

@app.route('/robohash/<s>', methods=['GET'])
def robohash_s(s):
    if request.method == 'GET':
        return robohash.get(request, session, s)
    else: abort(405)

@app.route('/test', methods=['GET'])
def test_():
    if request.method == 'GET':
        return test.do(request, session)
    else: abort(405)

@app.route('/vms', methods=['GET'])
def vms_():
    if request.method == 'GET':
        return vms.index(request, session)
    else: abort(405)

@app.route('/vms/new/', methods=['GET', 'POST'])
def vms_create():
    if request.method == 'GET':
        return vms.new(request, session)
    if request.method == 'POST':
        return vms.create(request, session)
    else: abort(405)

@app.route('/vms/<id>', methods=['GET'])
def vms_id(id):
    id = decode_id(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return vms.show(request, session, id)
    else: abort(405)

@app.route('/vms/<id>/edit', methods=['GET', 'POST'])
def vms_id_edit(id):
    id = decode(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return vms.edit(request, session, id)
    if request.method == 'POST':
        return vms.update(request, session, id)
    else: abort(405)

@app.route('/vms/<id>/delete', methods=['GET'])
def vms_id_delete(id):
    id = decode(id)
    if id == None: abort(404)
    if request.method == 'GET':
        return vms.delete(request, session, id)
    else: abort(405)

if __name__=='__main__':
    app.debug = True
    app.secret_key = globals.config['common']['secret']
    app.jinja_env.globals['app_name'] = config['common']['name']
    app.jinja_env.globals['app_tagline'] = config['common']['tagline']
    app.run(host='0.0.0.0', threaded=True)
