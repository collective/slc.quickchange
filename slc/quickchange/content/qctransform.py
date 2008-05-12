"""Definition of the QCTransform content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from slc.quickchange import quickchangeMessageFactory as _
from slc.quickchange.interfaces import IQCTransform
from slc.quickchange.config import PROJECTNAME

QCTransformSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

QCTransformSchema['title'].storage = atapi.AnnotationStorage()
QCTransformSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(QCTransformSchema, moveDiscussion=False)

class QCTransform(base.ATCTContent):
    """A change transform type"""
    implements(IQCTransform)

    portal_type = "QCTransform"
    schema = QCTransformSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(QCTransform, PROJECTNAME)
