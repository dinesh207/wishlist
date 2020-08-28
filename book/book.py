import logging
from flask import Blueprint
from flask import request
import sqlite3 as sql
from db.sqlite import get_db
from utils.utils import *

LOG = logging.getLogger(__name__)
book_blueprint = Blueprint('book', __name__)


class Book:
    @book_blueprint.route('/books', methods=['POST'])
    def add():
        book = request.get_json()
        # TODO: add validation
        try:
            db = get_db()
            cur = db.execute("INSERT into books(Title, Author, ISBN, DateOfPublication) values"
                             + "(?, ?, ?, ?)", (book['title'], book['author'], book['ISBN'], book['dateOfPublication']))
            db.commit()
            book['id'] = cur.lastrowid
        except sql.Error as e:
            db.rollback()
            LOG.error(e)
            return send_error_rest_response(status=500, message="Internal server error")

        return send_rest_response(200, {'id': book["id"], 'message': 'Book added successfully'})

    @book_blueprint.route('/books/<int:id>', methods=['GET'])
    def get(id):
        if id is None:
            return send_error_rest_response(400, "Book id must be provied")
        resultSet = []
        try:
            db = get_db()
            cur = db.execute("Select * from books where Id=?", [id])
            resultSet = cur.fetchall()
            cur.close()
        except Error as err:
            LOG.error(err)
            # Internal server error
            return send_error_rest_response(500, "Internal server error")
        if len(resultSet) == 0:
            LOG.info("Book not found with id: %s", email)
            return send_error_rest_response(404, "Book not found with id: " + id)
        book = resultSet[0]
        return send_rest_response(200, {'book': book})

    @book_blueprint.route('/books/<int:id>', methods=['PUT'])
    def update(id):
        # TODO: add validation on request
        book = request.get_json()
        try:
            db = get_db()
            cur = db.execute("UPDATE books SET Title=?, Author=?, ISBN=?, DateOfPublication=?",
                             (book['title'], book['author'], book['ISBN'], book['dateOfPublication']))
            db.commit()
            book['id'] = id
        except sql.Error as e:
            db.rollback()
            LOG.error(e)
            return send_error_rest_response(status=500, message="Internal server error")

        return send_rest_response(200, {'id': book["id"], 'message': 'Book updated successfully'})

    @book_blueprint.route('/books/<int:id>', methods=['DELETE'])
    def remove(id):
        if id is None:
            return send_error_rest_response(400, "Book id must be provied")
        try:
            db = get_db()
            cur = db.execute("DELETE from books where Id=?", [id])
            db.commit()
        except sql.Error:
            db.rollback()
            return send_error_rest_response(status=500, message="Internal server error")
        return send_rest_response(200, {'message': "Book deleted successfully"})
