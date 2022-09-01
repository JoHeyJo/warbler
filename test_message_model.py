"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from psycopg2 import IntegrityError

from models import db, User, Message, Follows, Like

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


class MessageModelTestCase(TestCase):
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
        # self.client = app.test_client()

        # message = Message(text = "Testing message", user_id = u.id)
        
    

    def test_message_model(self):
        """Testing if message is created"""
        
        message = Message(text = "Message to test user 2", user_id = self.user2.id)
        message.id = 5000
        db.session.add(message)
        db.session.commit()
        message2 = Message.query.get(5000)
        self.assertEqual(message2.text, "Message to test user 2")
        self.assertEqual(message2.user_id, self.user2.id)


    def test_mesage_likes(self):
        """Testing message likes"""
         
        message = Message(text = "Testing message", user_id = self.user.id)
        db.session.add(message)
        db.session.commit()

        self.user2.likes.append(message)
        db.session.commit()

        like = Like.query.filter(Like.user_id == self.user2.id).all()

        self.assertEqual(like[0].message_id, message.id)

    
    def test_mesage_like_delete(self):
        """Testing message like is removed"""
         
        message = Message(text = "Testing message", user_id = self.user.id)
        db.session.add(message)
        db.session.commit()

        self.user2.likes.append(message)
        db.session.commit()

        self.user2.likes.remove(message)
        db.session.commit()

        like = Like.query.filter(Like.user_id == self.user2.id).all()
        
        self.assertFalse(like)