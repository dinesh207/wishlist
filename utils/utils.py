from flask import Response
from flask import json


def send_error_rest_response(status, message):
    return Response(
        status=status,
        response=json.dumps({'message': message}),
        mimetype='application/json')


def send_rest_response(status, data):
    return Response(
        status=status,
        response=json.dumps(data),
        mimetype='application/json'
    )
