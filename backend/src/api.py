import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
@requires_auth('')
def get_drinks(payload):
    drinks_query = Drink.query.all()
    drinks = [drink.short() for drink in drinks_query]
    return jsonify({
        'success': True,
        'code': 200,
        'drinks': drinks,
    })


'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks_query = Drink.query.all()
    drinks = [drink.long() for drink in drinks_query]
    return jsonify({
        'success': True,
        'code': 200,
        'drinks': drinks,
    })


'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/create', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    drink = request.get_json()
    title = drink['title']
    recipe = drink['recipe']
    drink = Drink(title=title, recipe=json.dumps(recipe))
    drink.insert()
    drinks_query = Drink.query.all()
    drinks = [drink.short() for drink in drinks_query]
    return jsonify({
        'success': True,
        'code': 200,
        'drinks': drinks,
    })


'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/edit/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id,):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    drink_details = request.get_json()
    drink.title = drink_details['title']
    drink.recipe = json.dumps(drink_details['recipe'])
    drink.update()
    return jsonify({
        'success': True,
        'code': 200,
        'drinks': [drink.long()],
    })


'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/delete/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    drink.delete()
    return jsonify({
        'success': True,
        'code': 200,
        'delete': drink_id,
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "resource forbidden"
    }), 403


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": error.description
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": error.description
    }), 401
