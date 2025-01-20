from flask_login import UserMixin
from common.utils import JsonSerializable

class User(UserMixin, JsonSerializable):
    def __init__(self, cid, email, roles = []):
        self.cid = cid
        self.email = email
        #self.username = username
        # pseudo-serializer for loading from json (map dict role to Role)
        if roles and type(roles[0]) == dict:
            from roles.models import Role
            roles = [Role(**r) for r in roles]
        self.roles = roles
        self.authenticated = False
    def is_active(self):
        return self.is_active()
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return self.authenticated
    def is_active(self):
        return True
    def get_id(self):
        return str(self.cid)