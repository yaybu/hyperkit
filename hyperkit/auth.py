
class Auth(object):
    pass


class PasswordAuth(Auth):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class SSHAuth(Auth):
    def __init__(self, username, private_key, public_key):
        self.username = username
        self.private_key = private_key
        self.public_key = public_key

__all__ = [Auth, PasswordAuth, SSHAuth]
