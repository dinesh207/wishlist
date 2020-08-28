import logging
from flask import Blueprint
from flask import request
import sqlite3 as sql
from db.sqlite import get_db
from utils.utils import *

LOG = logging.getLogger(__name__)
user_blueprint = Blueprint('user', __name__)


class User:

    @user_blueprint.route('/users', methods=['POST'])
    def add():
        user = request.get_json()
        # TODO: add validation
        try:
            db = get_db()
            cur = db.execute("INSERT into users(FirstName, LastName, Email, Password) values"
                             + "(?, ?, ?, ?)", (user['firstName'], user['lastName'], user['email'], user['password']))
            db.commit()
            user["id"] = cur.lastrowid
        except sql.IntegrityError as err:
            db.rollback()
            return send_error_rest_response(status=409, message="User already exists")
        except sql.Error:
            db.rollback()
            return send_error_rest_response(status=500, message="Internal server error")

        return send_rest_response(200, {'id': user["id"], 'message': 'User added successfully'})

    @user_blueprint.route('/users/<int:id>', methods=['GET'])
    def get(id):
        if id is None:
            return send_error_rest_response(400, "User id must be provied")
        resultSet = []
        try:
            db = get_db()
            cur = db.execute(
                "Select users.Id, users.FirstName, users.LastName, users.Email from users where Id=?", [id])
            resultSet = cur.fetchall()
            cur.close()
        except sql.Error as err:
            LOG.error(err)
            # Internal server error
            return send_error_rest_response(500, "Internal server error")
        if len(resultSet) == 0:
            LOG.info("User not found with Id: %s", str(id))
            return send_error_rest_response(404, "User not found with Id: " + str(id))

        user = resultSet[0]
        return send_rest_response(200, {'user': resultSet[0]})

    @user_blueprint.route('/users/<int:id>', methods=['DELETE'])
    def remove(id):
        if id is None:
            return send_error_rest_response(400, "User id must be provied")
        try:
            db = get_db()
            cur = db.execute("DELETE from users where Id=?", [id])
            db.commit()
        except sql.Error:
            db.rollback()
            return send_error_rest_response(status=500, message="Internal server error")
        return send_rest_response(200, {'message': "User deleted successfully"})
