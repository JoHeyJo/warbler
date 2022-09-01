"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None
        )

        self.testuser2 = User.signup(email="test2@test2.com",
                              username="testuser2",
                              password="HASHED_PASSWORD",
                              image_url=None
        )
        self.testuser3 = User.signup(email="test3@test3.com",
                              username="testuser3",
                              password="HASHED_PASSWORD",
                              image_url=None
        )
        self.testuser.id = 100
        self.testuser_id = self.testuser.id
        self.testuser2.id = 200
        self.testuser2_id = self.testuser2.id
        self.testuser3.id = 300
        self.testuser3_id = self.testuser3.id
        db.session.commit()

        follow = Follows(user_being_followed_id=self.testuser_id, 
                          user_following_id=self.testuser2_id)
        
        follow2 = Follows(user_being_followed_id=self.testuser3_id, 
                          user_following_id=self.testuser2_id)
        
        db.session.add(follow)
        db.session.add(follow2)
        db.session.commit()


    def test_following_page(self):
        """Testing: can you see the following pages for any user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser2_id}/following")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)

    def test_follower_page(self):
        """Testing: can you see the followers pages for any user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/followers")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser2", html)

    def test_unauthorized_following(self):
        """Testing unauthorized following"""

        with self.client as c:  
          
            resp = c.get(f"/users/{self.testuser_id}/followers")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 302)
            self.assertNotIn("testuser2", html)

    def test_following_youself(self):
        """Test following youself"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f'/users/follow/{self.testuser_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("You can not follow yourself!!!", html)
