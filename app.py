from flask import Flask

from db.sqlite import init_db
from user.user import user_blueprint
from user.wishlist import wishlist_blueprint
from book.book import book_blueprint


def create_app():
    # app initializing
    app = Flask(__name__)
    app.register_blueprint(wishlist_blueprint)
    app.register_blueprint(book_blueprint)
    app.register_blueprint(user_blueprint)
    app.config.from_pyfile('config.cfg')
    with app.app_context():
        init_db()
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
