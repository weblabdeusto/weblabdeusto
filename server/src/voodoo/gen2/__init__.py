from .parser import load, loads
from .locator import Locator
from .address import CoordAddress

assert load is not None and loads is not None # Avoid pyflakes
assert Locator is not None # Avoid pyflakes
assert CoordAddress is not None # Avoid pyflakes
