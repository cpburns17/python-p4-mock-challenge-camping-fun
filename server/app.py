#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return 'campers'

@app.get('/campers')
def get_camper():
    campers = Camper.query.all()
    campers_list = []
    for c in campers:
        campers_list.append(c.to_dict(rules = ('-signups',)))
    return campers_list

@app.get('/campers/<int:id>')
def get_camper_id(id):
    camper = db.session.get(Camper, id)

    if not camper:
        return {'error':'Camper not found'}, 404
    else:
        return camper.to_dict()
    
@app.post('/campers')
def post_camper():

    try:
        data = request.json
        camper = Camper(name = data.get('name'), age = data.get('age'))
        db.session.add(camper)
        db.session.commit()

        return camper.to_dict(), 200
    
    except Exception as e:
        return {'errors': ['validation errors']}, 400    
    

@app.patch('/campers/<int:id>')
def update_camper(id):

    try:
        data = request.json
        camper = db.session.get(Camper, id)
        if not camper:
            return {'error': 'Camper not found'}, 404
        for key in data:
            setattr(camper, key, data[key])
            db.session.add(camper)
            db.session.commit()

        return camper.to_dict(rules = ['-signups']), 202

    except Exception as e:
        return {'errors': ['validation errors']}, 400
    

@app.get('/activities')
def get_activities():
    activities = Activity.query.all()
    activity_list = []
    for a in activities:
        activity_list.append(a.to_dict(rules = ('-signups',)))

    return activity_list

@app.delete('/activities/<int:id>')
def delete_activity(id):
    activity = db.session.get(Activity, id)

    if not activity:
        return {'error': 'Activity not found'}, 404
    
    db.session.delete(activity)
    db.session.commit()
    return {}, 204

@app.get('/signups')
def get_signups():
    signups = Signup.query.all()
    signup_list = []
    for s in signups:
        signup_list.append(s.to_dict(rules = ('-activity', '-camper')))

    return signup_list

@app.post('/signups')
def add_signup():
    data = request.json

    try:
        signup = Signup(camper_id = data.get('camper_id'), activity_id = data.get('activity_id'), time = data.get('time'))
        db.session.add(signup)
        db.session.commit()
    
        return signup.to_dict(), 200
    
    except Exception as e:
        return {'errors': ['validation errors']}, 400



if __name__ == '__main__':
    app.run(port=5555, debug=True)
