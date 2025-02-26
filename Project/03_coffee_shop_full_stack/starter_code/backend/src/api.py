import os, sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
# @requires_auth('get:drinks')
def get_drinks():
    try: 
        # print(f'JWT: {payload}')
        print(f'DRINKS: {Drink.query.order_by(Drink.id).all()}')
        drinks = [ drink.short() for drink in Drink.query.order_by(Drink.id).all() ]
        if len(drinks) == 0 or drinks == None:
            abort(404)
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except Exception:

        abort(400)

    


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try: 
        drinks_details = [ drink.long() for drink in Drink.query.order_by(Drink.id).all() ]
        if len(drinks_details) == 0 or drinks_details == None:
            abort(404)
        return jsonify({
            'status': 200,
            'success': True,
            'drinks': drinks_details
        })
    except Exception:

        abort(400)



'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    try:
        request_data = request.get_json()
        title = request_data['title']
        recipe = json.dumps([request_data['recipe']])
        print(f'RECIPE {recipe}')
        new_drink = Drink(title, recipe)
        print(f'NEW DRINK: {new_drink}')

        new_drink.insert()

        return jsonify({
            'success': True,
            # 'drinks': Drink.query.filter(Drink.id == new_drink.id)
        })
    except Exception:
        print(sys.exc_info())
        abort(422)



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    try:

        drink = Drink.query.filter(Drink.id == id).one_or_none()
        print(f'THE DRINK: {drink}')
        if drink is None:
            abort(404)
        request_data = request.get_json()
        print(f'REQUEST_DATA: {request_data}')
        print(request_data['title'])
        drink.title = request_data['title']
        print(drink.title)
        print(f'DRINK: {drink}')
        print(type(drink))
        drink.update()
        updated_drink = [drink.serialize()]
        print(f'UPDATED DRINK: {updated_drink}')
        return jsonify({
            'success': True,
            'drinks': updated_drink
        })
    
    except Exception:
        print(sys.exc_info())
        abort(400)
    


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        
        drink.delete()
        return jsonify({
            'success': True,
            'drinks': id
        })
    
    except Exception:
        abort(422)


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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "Sorry, nothing found"
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
    })


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authError(e):
    return jsonify(e.error), e.status_code
