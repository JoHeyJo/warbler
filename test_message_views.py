"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

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
                                    image_url=None)
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="tes2t@test2.com",
                                    password="testuser2",
                                    image_url=None)



        self.testuser2.id = 200
        self.testuser2_id = self.testuser2.id
        db.session.commit()

        
    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    def test_delete_message(self):
        """Test if messags deletes"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id


            resp = c.post("/messages/new", data={"text": "Hello"})

            msg = Message.query.one()
            
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Hello", html)
    
    def test_message_authorization_add(self):
        """Test can you add a message when logged out. Should be False"""

        with self.client as c:
            
            resp = c.post("/messages/new", data={"text": "Hello"}, 
                                            follow_redirects=True)
            
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            
    def test_message_authorization_delete(self):
        """Can message be deleted when not logged in?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            msg = Message.query.one()
            
            c.post("/logout")
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            
    # def test_add_message_as_another_user(self):
    #     """Testing adding a message as another user while logged in"""
        
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id

    #         resp = c.post("/messages/new", data={"text": "Hello"}, 
    #                                         follow_redirects=True)
            
    #         html = resp.get_data(as_text=True)
            
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Access unauthorized.", html)
    
    def test_delete_message_as_another_user(self):
        """Can user delete a message not associated to them"""
        
        msg = Message(id = 300, 
                    text="Testing text",
                    user_id = self.testuser2_id)
        db.session.add(msg)
        db.session.commit()
            
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post("/messages/300/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)