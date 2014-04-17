
class Auth(object):
    pass


class PasswordAuth(Auth):
    def __init__(self, username="hyperkit", password="password"):
        self.username = username
        self.password = password

    def __str__(self):
        return "password authentication for username '%s'" % (self.username, )


class SSHAuth(Auth):
    def __init__(self, username, public_key, private_key=None):
        self.username = username
        self.public_key = public_key
        self.private_key = private_key

    def __str__(self):
        return "SSH authentication using public key file '%s'" % (self.public_key, )

__all__ = [Auth, PasswordAuth, SSHAuth]
