"""Definition of the QCJob content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from slc.quickchange import quickchangeMessageFactory as _
from slc.quickchange.interfaces import IQCJob
from slc.quickchange.config import PROJECTNAME

QCJobSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

QCJobSchema['title'].storage = atapi.AnnotationStorage()
QCJobSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(QCJobSchema, folderish=True, moveDiscussion=False)

class QCJob(folder.ATFolder):
    """A Change Job"""
    implements(IQCJob)

    portal_type = "QCJob"
    schema = QCJobSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(QCJob, PROJECTNAME)
