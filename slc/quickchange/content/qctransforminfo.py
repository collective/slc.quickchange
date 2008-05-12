"""Definition of the QCTransformInfo content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from slc.quickchange import quickchangeMessageFactory as _
from slc.quickchange.interfaces import IQCTransformInfo
from slc.quickchange.config import PROJECTNAME

QCTransformInfoSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

QCTransformInfoSchema['title'].storage = atapi.AnnotationStorage()
QCTransformInfoSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(QCTransformInfoSchema, moveDiscussion=False)

class QCTransformInfo(base.ATCTContent):
    """Description of the Example Type"""
    implements(IQCTransformInfo)

    portal_type = "QCTransformInfo"
    schema = QCTransformInfoSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(QCTransformInfo, PROJECTNAME)
