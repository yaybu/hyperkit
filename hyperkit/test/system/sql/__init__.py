
import os


def load(filename):
    here = os.path.dirname(__file__)
    return open(os.path.join(here, filename)).read()

create = load("create.sql")
