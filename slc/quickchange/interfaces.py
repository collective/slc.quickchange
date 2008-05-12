from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from slc.quickchange import quickchangeMessageFactory as _

# -*- extra stuff goes here -*-

class IQCTransformInfo(Interface):
    """Description of the Example Type"""

class IQCTransform(Interface):
    """A change transform type"""

class IQCJob(Interface):
    """A Change Job"""
