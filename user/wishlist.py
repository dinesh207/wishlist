import logging
from flask import Blueprint
from flask import request
import sqlite3 as sql
from db.sqlite import get_db
from utils.utils import *

LOG = logging.getLogger(__name__)
wishlist_blueprint = Blueprint('wishlist', __name__)


class Wishlist:
    @wishlist_blueprint.route('/users/wishlist', methods=['POST'])
    def add():
        whishlist = request.get_json()
        try:
            db = get_db()
            cur = db.execute("INSERT into wishlist(UserId, BookId) values"
                             + "(?, ?)", (whishlist["userId"], whishlist["bookId"]))
            db.commit()
        except sql.IntegrityError as err:
            db.rollback()
            if 'FOREIGN' in str(err):
                return send_error_rest_response(400,
                                                "User/Book doesn't exists with UserId: " + str(whishlist["userId"]) + ", BookId: " + str(whishlist["bookId"]))
            return send_error_rest_response(status=409, message="Wishlist already exists")
        except sql.Error:
            db.rollback()
            return send_error_rest_response(status=500, message="Internal server error")

        return send_rest_response(200, {'message': 'Wishlist added successfully'})

    @wishlist_blueprint.route('/users/<int:id>/wishlist', methods=['GET'])
    def get(id):
        if id is None:
            return send_error_rest_response(400, "User id must be provied")
        resultSet = []
        try:
            db = get_db()
            cur = db.execute("SELECT users.FirstName, users.LastName, users.Email, " +
                             "json_group_array(json_object('Title', books.title, 'Author', books.author, 'ISBN', books.ISBN)) as 'WishList'" +
                             "FROM WishList, users, books where UserId = ? " +
                             "AND UserId = users.Id AND BookId =books.Id", [id])
            resultSet = cur.fetchall()
            cur.close()
        except sql.Error as err:
            LOG.error(err)
            # Internal server error
            return send_error_rest_response(500, "Internal server error")
        if len(resultSet) == 0:
            LOG.info("Whishlist not found with user Id: %s", str(id))
            return send_error_rest_response(404, "Whishlist not found with user Id: %s", str(id))

        return send_rest_response(200, resultSet[0])

    @wishlist_blueprint.route('/users/<int:id>/book/<int:book_id>', methods=['DELETE'])
    def remove(id, book_id):
        try:
            db = get_db()
            cur = db.execute(
                "DELETE from Wishlist where UserId=? and BookId=?", (id, book_id))
            db.commit()
        except sql.Error:
            db.rollback()
            return send_error_rest_response(status=500, message="Internal server error")
        return send_rest_response(200, {'message': "Wishlist removed successfully"})
