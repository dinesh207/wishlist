import unittest
import json

from app import create_app
from db.sqlite import get_db, init_db, close_db

TEST_DB = 'sqlite/test.db'


class WhishListTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['DATABASE'] = TEST_DB
        with self.app.app_context():
            init_db()
        self.client = self.app.test_client()

    # This can be broken into multiple parts
    def test_managing_whishlist(self):
        # Add users
        response = self.addUser()
        userId = response.json['id']
        print("User ID: " + str(userId))
        self.assertEqual(200, response.status_code)
        self.assertEqual(int, type(userId))

        # Create Books
        book = json.dumps({
            "title": "Maths",
            "author": "Rob",
            "ISBN": "1234",
            "dateOfPublication": "12/01/2019"
        })
        response = self.client.post(
            '/books', headers={"Content-Type": "application/json"}, data=book)
        bookId1 = response.json['id']
        print("Book ID1: " + str(bookId1))
        self.assertEqual(200, response.status_code)
        self.assertEqual(int, type(bookId1))

        book = json.dumps({
            "title": "Algebra",
            "author": "John",
            "ISBN": "11",
            "dateOfPublication": "01/02/2018"
        })
        response = self.client.post(
            '/books', headers={"Content-Type": "application/json"}, data=book)
        bookId2 = response.json['id']
        print("Book ID2: " + str(bookId2))
        self.assertEqual(200, response.status_code)
        self.assertEqual(int, type(bookId2))

        # Add wishlist
        reqData = json.dumps({
            "userId": userId,
            "bookId": bookId1
        })
        # Add whishlist
        response = self.client.post(
            '/users/wishlist', headers={"Content-Type": "application/json"}, data=reqData)
        self.assertEqual('Wishlist added successfully',
                         response.json['message'])
        self.assertEqual(200, response.status_code)

        reqData = json.dumps({
            "userId": userId,
            "bookId": bookId2
        })
        # Add whishlist
        response = self.client.post(
            '/users/wishlist', headers={"Content-Type": "application/json"}, data=reqData)
        self.assertEqual('Wishlist added successfully',
                         response.json['message'])
        self.assertEqual(200, response.status_code)

        # Try adding to non existing book
        reqData = json.dumps({
            "userId": 3,
            "bookId": bookId2
        })
        # Add whishlist should through bad request
        response = self.client.post(
            '/users/wishlist', headers={"Content-Type": "application/json"}, data=reqData)
        self.assertEqual("User/Book doesn't exists with UserId: 3, BookId: " + str(bookId2),
                         response.json['message'])
        self.assertEqual(400, response.status_code)

        # Clear the data
        response = self.client.delete(
            '/users/' + str(userId) + '/book/' + str(bookId1))
        self.assertEqual(200, response.status_code)

        response = self.client.delete(
            '/users/' + str(userId) + '/book/' + str(bookId2))
        self.assertEqual(200, response.status_code)

        response = self.client.delete('/users/' + str(userId))
        self.assertEqual(200, response.status_code)

        response = self.client.delete('/books/' + str(bookId1))
        self.assertEqual(200, response.status_code)

        response = self.client.delete('/books/' + str(bookId2))
        self.assertEqual(200, response.status_code)

    def test_updating_wishlist(self):
        response = self.addUser()
        userId = response.json['id']
        self.assertEqual(200, response.status_code)
        self.assertEqual(int, type(userId))
        # Create book
        book = json.dumps({
            "title": "Test book",
            "author": "test",
            "ISBN": "123455",
            "dateOfPublication": "08/27/2020"
        })
        response = self.client.post(
            '/books', headers={"Content-Type": "application/json"}, data=book)
        bookId = response.json['id']
        print("Book ID: " + str(bookId))
        self.assertEqual(200, response.status_code)
        self.assertEqual(int, type(bookId))

        # Add to wishlist
        reqData = json.dumps({
            "userId": userId,
            "bookId": bookId
        })
        response = self.client.post(
            '/users/wishlist', headers={"Content-Type": "application/json"}, data=reqData)
        self.assertEqual('Wishlist added successfully',
                         response.json['message'])
        self.assertEqual(200, response.status_code)

        # Get user wishlist
        response = self.client.get(
            '/users/' + str(userId) + '/wishlist', headers={"Content-Type": "application/json"})
        self.assertEqual(200, response.status_code)
        wishlist = response.json
        self.assertEqual("TestUser", wishlist["FirstName"])
        self.assertEqual("Test", wishlist["LastName"])
        self.assertEqual("test@gmail.com", wishlist["Email"])
        self.assertEqual(1, len(wishlist['WishList']))
        self.assertEqual("test", wishlist['WishList'][0]["Author"])
        self.assertEqual("Test book", wishlist['WishList'][0]["Title"])
        self.assertEqual("123455", wishlist['WishList'][0]["ISBN"])

        # Update book
        reqData = json.dumps({
            "title": "Updated Title",
            "author": "Updated author",
            "ISBN": "123",
            "dateOfPublication": "08/27/2020"
        })
        response = self.client.put(
            '/books/' + str(bookId), headers={"Content-Type": "application/json"}, data=reqData)
        updatedBookId = response.json['id']
        print("Updated Book ID: " + str(updatedBookId))
        self.assertEqual(200, response.status_code)
        self.assertEqual(int, type(updatedBookId))
        self.assertEqual(bookId, updatedBookId)

        # Verify update
        response = self.client.get(
            '/users/' + str(userId) + '/wishlist', headers={"Content-Type": "application/json"})
        self.assertEqual(200, response.status_code)
        wishlist = response.json
        self.assertEqual("TestUser", wishlist["FirstName"])
        self.assertEqual("Test", wishlist["LastName"])
        self.assertEqual("test@gmail.com", wishlist["Email"])
        self.assertEqual(1, len(wishlist['WishList']))
        self.assertEqual("Updated author", wishlist['WishList'][0]["Author"])
        self.assertEqual("Updated Title", wishlist['WishList'][0]["Title"])
        self.assertEqual("123", wishlist['WishList'][0]["ISBN"])

        # Remove wishlist
        response = self.client.delete(
            '/users/' + str(userId) + '/book/' + str(bookId))
        self.assertEqual(200, response.status_code)

        response = self.client.delete('/users/' + str(userId))
        self.assertEqual(200, response.status_code)

        response = self.client.delete('/books/' + str(bookId))
        self.assertEqual(200, response.status_code)

    def addUser(self):
        user = json.dumps({
            "firstName": "TestUser",
            "lastName": "Test",
            "email": "test@gmail.com",
            "password": "test"
        })
        response = self.client.post(
            '/users', headers={"Content-Type": "application/json"}, data=user)
        return response

    def tearDown(self):
        with self.app.app_context():
            db = get_db()
            db.execute("DELETE from Wishlist")
            db.execute("DELETE from Users")
            db.execute("DELETE from Books")
            db.commit()
            close_db()


if __name__ == '__main__':
    unittest.main()
