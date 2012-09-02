from .meta import Session, metadata
from .objects import *

def init(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
