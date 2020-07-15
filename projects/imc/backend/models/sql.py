""" CUSTOM Models for the relational database """

from restapi.models.sql import User, db

# Add (inject) attributes to User
setattr(User, "my_custom_field", db.Column(db.String(255)))
