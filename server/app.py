#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):

    def post(self):
        data = request.get_json()
        try:
            user = User(
                username=data['username'],
                image_url=data['image_url'],
                bio=data['bio']
            )
            user.password_hash = data['password']

            session['user_id'] = user.id

            db.session.add(user)
            db.session.commit()

            return user.to_dict(), 201
        except ValueError as e:
            return {'error': 'Failed Validation'}, 422

class CheckSession(Resource):

    def get(self):
        user = User.query.where(User.id == session['user_id']).first()
        if user:
            return user.to_dict(), 200
        return {'error': 'unauthorized'}, 401

class Login(Resource):
    
    def post(self):
        user = User.query.where(User.username == request.json.get('username')).first()
        if user and user.authenticate(request.json.get('password')):
            session['user_id'] = user.id
            return user.to_dict()
        else:
            return {'error': 'Invalid username or password'}, 401

class Logout(Resource):

    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            return {}, 204
        return {'error': 'not authorized'}, 401

class RecipeIndex(Resource):

    def get(self):
        if session['user_id']:
            user = User.query.where(User.id == session.get('user_id')).first()
            if user.recpies:
                return [r.to_dict() for r in user.recipes], 200
            return {'error'}, 422
        
        else:
            return {'error'}, 401
        
    def post(self):
        # Check if 'user_id' is in the session
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'user_id not found in session'}, 400

        # Retrieve the user instance using session['user_id']
        user = User.query.where(User.id == user_id).first()

        if user:
            # Create a new Recipe object with data from the request
            r = Recipe(
                title=request.json.get('title'),
                instructions=request.json.get('instructions'),
                minutes_to_complete=request.json.get('minutes_to_complete')
            )

            # Set the user attribute to the retrieved user instance
            r.user = user

            # Add the recipe to the session and commit it
            db.session.add(r)
            db.session.commit()

            return r.to_dict(), 201
        return {'error': 'user not found'}, 404


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)