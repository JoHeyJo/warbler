"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from psycopg2 import IntegrityError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        self.user2 = u2
        self.user = u
        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test1@test.com",
            username="test1user",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        self.user = u

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_user_repr(self):
        """Does the repr Method Work"""

        self.assertEqual(self.user.__repr__(),
        f"<User #{self.user.id}: {self.user.username}, {self.user.email}>")


    def test_is_not_following(self):
        """Does is following method work when not following"""

        self.assertFalse(self.user.is_following(self.user2))


    def test_is_following(self):
        """Does is following method work"""

        self.user.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user.is_following(self.user2))

    
    def test_is_not_followed_by(self):
        """Does is followed by method work when not followed"""

        self.assertFalse(self.user.is_followed_by(self.user2))


    def test_is_followed_by(self):
        """Does is followed by method work"""

        self.user2.following.append(self.user)
        db.session.commit()

        self.assertTrue(self.user.is_followed_by(self.user2))

    
    def test_user_signup(self):
        """Does User signup successfully create a new user"""

        user1 = User.signup('new_user', 'new_email', '123456', 'http://google.com')
        user1.id = 5000
        db.session.commit()
        
        user = User.query.get(5000)
        self.assertEqual(user.username, "new_user")
        self.assertEqual(user.email, "new_email")
        self.assertEqual(user.image_url, 'http://google.com')


    def test_user_signup_fail(self):
        """Does User signup fail if fields fail"""  
        
        try:
            user = User.signup("testuser2",
            "test2@test.com", 
            "HASHED_PASSWORD",
            "google"
            )
            db.session.commit()
        except:
            error = "Email already exists"

        self.assertTrue(error)

    
    def test_user_authenticate(self):
        """Does authenticate return a user given username and password"""

        test_user = User.signup('new_user', 'new_email', '123456', 'http://google.com')
        user = User.authenticate("new_user", "123456")

        self.assertEqual(user, test_user)

    
    def test_user_authenticate_username_fail(self):
        """Does authenticate fail to return a user given wrong username and password"""

        test_user = User.signup('new_user', 'new_email', '123456', 'http://google.com')
        user = User.authenticate("new_user2", "123456")

        self.assertFalse(user, test_user)


    def test_user_authenticate_password_fail(self):
        """Does authenticate fail to return a user given username and wrong password"""

        test_user = User.signup('new_user', 'new_email', '123456', 'http://google.com')
        user = User.authenticate("new_user", "BADPASSWORD7")

        self.assertFalse(user, test_user)

