
import os

__all__ = []

here = os.path.dirname(__file__)
for f in os.listdir(here):
    if f.endswith(".sql"):
        name = f[:-4]
        pathname = os.path.join(here, f)
        globals()[name] = open(pathname).read()
        __all__.append(name)
