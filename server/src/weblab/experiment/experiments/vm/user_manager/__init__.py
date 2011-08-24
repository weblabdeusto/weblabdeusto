
import UserManager
import dummy as DummyUserManager
import HttpQueryUserManager

def _():
    print UserManager, DummyUserManager, HttpQueryUserManager # Avoid unused warnings

__all__ = ["UserManager", "DummyUserManager", "HttpQueryUserManager"]