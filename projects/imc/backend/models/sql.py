# -*- coding: utf-8 -*-

""" CUSTOM Models for the relational database """

from restapi.models.sql import db, User

# Add (inject) attributes to User
setattr(User, 'my_custom_field', db.Column(db.String(255)))
