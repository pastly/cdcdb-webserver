from flask import abort
from flask import redirect
from flask import render_template
from flask import url_for
from datetime import datetime, timedelta
from os import urandom
import json

from database_connection import DatabaseConnection
from globals import globals

# Handles the Presentations routes.

class Presentations:
    def __init__(self):
        self.b58 = globals.base58_hashids
        self.encode_id = globals.encode_id

    #####
    # PERMISSION CHECKS
    #####

    def __can_index(self, session):
        return True

    def __can_show(self, session):
        return True

    def __can_edit(self, session):
        return 'is_officer' in session and session['is_officer']

    def __can_update(self, session):
        return 'is_officer' in session and session['is_officer']

    def __can_create(self, session):
        return 'is_officer' in session and session['is_officer']

    def __can_delete(self, session):
        return 'is_officer' in session and session['is_officer']

    # Get all presentations in the db
    def __db_get_presentations(self):
        with DatabaseConnection() as db:
            presentations, _ = db.get_table("presentation")
            pres_pers,_ = db.get_table("presenters")
            people,_ = db.get_table("people_read")
            q = db.query().\
                add_columns(
                    presentations.c.id, presentations.c.name,
                    presentations.c.slides, pres_pers.c.person_id, people.c.full_name).\
                outerjoin(pres_pers, pres_pers.c.presentation_id == presentations.c.id).\
                outerjoin(people, people.c.id == pres_pers.c.person_id)
            db.execute(q)
            presentations = [ self.encode_id(dict(row), 'presentation_id') for row in db.fetchall() ]
            return presentations[::-1]

    # Get the presentation with the given id
    def __db_get_presentation(self, id):
        with DatabaseConnection() as db:
            presentations, _ = db.get_table("presentation")
            pres_pers,_ = db.get_table("presenters")
            people,_ = db.get_table("people_read")
            q = db.query().\
                add_columns(
                    presentations.c.id, presentations.c.name,
                    presentations.c.slides, pres_pers.c.person_id, people.c.full_name).\
                filter(presentations.c.id == id).\
                outerjoin(pres_pers, pres_pers.c.presentation_id == presentations.c.id).\
                outerjoin(people, people.c.id == pres_pers.c.person_id)
            db.execute(q)
            rows = [ self.encode_id(dict(row), 'presentation_id') for row in db.fetchall() ]
            if len(rows) != 1: return None
            return rows[0]

    # Insert a new presentation row
    def __db_insert_presentation(self, data):
        with DatabaseConnection() as db:
            presentations, _ = db.get_table("presentation")
            q = presentations.insert().\
                returning(presentations.c.id).\
                values(
                    name=data['name'],
                    slides=data['slides'])
            db.execute(q)
            lastrowid = db.lastrowid()
            if len(lastrowid) != 1: return None
            else:
                pres_pers,_ = db.get_table("presenters")
                q = pres_pers.insert().\
                    returning(pres_pers.c.presentation_id).\
                    values(
                        presentation_id=lastrowid[0],
                        person_id=data['presenter_id']
                    )
                return lastrowid[0]
                
    # Be lazy and just delete and readd
    def __db_update_presentation(self, data):
        self.__db_delete_presentation(data['id'])
        self.__db_insert_presentation(data)

    # Remove the presentation with the given id
    def __db_delete_presentation(self, id):
        with DatabaseConnection() as db:
            presentations, _ = db.get_table("presentation")
            q = presentations.delete().\
                where(presentations.c.id == id)
            db.execute(q)

    # Parse the data given, validate, and return the data with any errors
    def __validate_presentation(self, data):
        errs = []
        d = {}
        d['name'] = data['name']
        d['slides'] = data['slides']
        d['presenter_id'] = data['presenter_id']
        return d,errs

    # layer between create() and db functions
    def __create_presentation(self, request, session, data):
        v_data, errs = self.__validate_presentation(data)
        if errs:
            return render_template('presentations/new.html', data=data,
                errors=errs, submit_button_text='Create')
        id = self.__db_insert_presentation(v_data)
        id = self.b58.encode(id)
        return redirect(url_for('presentations_id', id=id))

    # layer between update() and db funcs
    def __update_presentation(self, request, session, id, data):
        v_data, errs = self.__validate_presentation(data)
        if errs:
            return render_template('presentations/new.html', data=data,
                errors=errs, submit_button_text='Update')
        v_data['id'] = id
        id = self.__db_update_presentation(v_data)
        id = self.b58.encode(id)
        return redirect(url_for('presentations_id', id=id))


    # Router calls this to show all presentations
    def index(self, request, session):
        if request.method == 'GET':
            if not self.__can_index(session): abort(403)
            presentations = self.__db_get_presentations()
            return render_template('presentations/index.html', presentations=presentations,
                can_create=self.__can_create(session),
                can_edit=self.__can_edit(session),
                can_delete=self.__can_delete(session))
        abort(405)

    # Router calls this to show an single presentation
    def show(self, request, session, id):
        if request.method == 'GET':
            if not self.__can_show(session): abort(403)
            presentation = self.__db_get_presentation(id)
            if not presentation: abort(404)
            return render_template('presentations/show.html', presentation=presentation,
                can_edit=self.__can_edit(session),
                can_delete=self.__can_delete(session))
        abort(405)

    # Router calls this to return new presentation form
    def new(self, request, session):
        if request.method == 'GET':
            if not self.__can_create(session): abort(403)
            return render_template('presentations/new.html',
                data={}, submit_button_text='Create')
        abort(405)

    # Router calls this to process a new presentation form
    def create(self, request, session):
        if request.method == 'POST':
            if not self.__can_create(session): abort(403)
            data = request.form
            return self.__create_presentation(request, session, data)
        abort(405)

    # Router calls this to return edit presentation form
    def edit(self, request, session, id):
        if request.method == 'GET':
            if not self.__can_edit(session): abort(403)
            pres = self.__db_get_presentation(id)
            data = {}
            data['name'] = pres['presentation_name']
            data['slides'] = pres['presentation_slides']
            print(pres)
            return render_template('presentations/new.html', data=data,
                submit_button_text='Update')
        abort(405)

    # Router calls this to process an edit presentation form
    def update(self, request, session, id):
        if request.method == 'POST':
            if not self.__can_update(session): abort(403)
            data = request.form
            return self.__update_presentation(request, session, id, data)
        abort(405)

    # Router calls this to delete the presentation with the given id
    def delete(self, request, session, id):
        if request.method == 'GET':
            if not self.__can_delete(session): abort(403)
            self.__db_delete_presentation(id)
            return redirect(url_for('events_'))

