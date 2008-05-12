"""
Uses standard reindexObject call on an object
"""
from Products.QuickChangeTool.interface.IQCTransform import IQCTransform
from Products.QuickChangeTool.QCTransform import QCTransform
from Products.QuickChangeTool.config import getCatalog
from Products.CMFDefault.utils import bodyfinder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import aq_base, aq_parent, aq_inner
import os


class ReindexObject(QCTransform):
    """ The ReindexObject Transform performs a simple Reindex on the given Object.
    """
    __implements__ = IQCTransform
    __transform_name__ = "ReindexObject"
    __widget__ = "QCTransformWidgets/ReindexObject"
        
    def apply(self, object, params={}):
        """ apply reindexObject on object """
        ob = aq_base(object)
        pc = getCatalog(self)
        if hasattr(ob, 'reindexObject'):
            object.reindexObject()
            return "reindexObject applied"
        elif hasattr(ob, 'reindex_object'):
            object.reindex_object()
            return "reindex_object applied"
        return "no reindex applied"            
            
    def __init__(self, id=''):
        QCTransform.__init__(self)        
        
def register():
    return ReindexObject()
