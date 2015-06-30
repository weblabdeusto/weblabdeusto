from __future__ import print_function, unicode_literals
from .parser import loads, load, load_dir
from .locator import Locator
from .address import CoordAddress

assert load is not None and loads is not None and load_dir is not None # Avoid pyflakes
assert Locator is not None # Avoid pyflakes
assert CoordAddress is not None # Avoid pyflakes
