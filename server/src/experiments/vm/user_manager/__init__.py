
import manager as UserManager
import dummy as DummyUserManager
import http as HttpQueryUserManager

def _():
    print UserManager, DummyUserManager, HttpQueryUserManager # Avoid unused warnings

__all__ = ["UserManager", "DummyUserManager", "HttpQueryUserManager"]
