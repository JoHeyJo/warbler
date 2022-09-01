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


        self.testuser.id = 500
        self.testuser_id = self.testuser.id
        self.testuser2.id = 200
        self.testuser2_id = self.testuser2.id
        db.session.commit()

        msg = Message(id = 300, 
                    text="Testing text",
                    user_id = self.testuser2_id)
        db.session.add(msg)
        db.session.commit()
        self.msg_id = 300

    def test_user_like(self):
        """Test that a user can like a message"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post('/messages/300/like', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            user = User.query.get(self.testuser_id)
            like = user.likes[0]
            self.assertEqual(like.id, self.msg_id)
