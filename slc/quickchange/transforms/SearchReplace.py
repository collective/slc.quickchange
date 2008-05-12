"""
Uses standard SearchReplace on the content of an object
"""
from Products.QuickChangeTool.interface.IQCTransform import IQCTransform
from Products.QuickChangeTool.QCTransform import QCTransform
from Products.CMFDefault.utils import bodyfinder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Acquisition import aq_base, aq_parent, aq_inner
import os, re
from types import UnicodeType, StringType


class SearchReplace(QCTransform):
    """ The Search & Replace Transforms can search for a given string and replace it by another string. The Matching is literal and does not use regular expressions
    """

    __implements__ = IQCTransform
    __transform_name__ = "SearchReplace"
    __widget__ = "QCTransformWidgets/SearchReplace"



    def apply(self, object, params={}):
        """ apply a Search & Replace on the content of an object """
        STATE = 0 # Describes if a pattern has been found in this object. If it has been found it'll also be replaced, so we can use this for both search and replace mode.
        #print "Applying Search and replace on ", object.getId(), "/".join(object.getPhysicalPath())
        srch = params.get('search')
        rep = params.get('replace')
        search_only = params.get('search_only')
        CHANGED = 0
        ob = aq_base(object)
        PTYPE = ob.portal_type
        MTYPE = ob.meta_type
        regexp = params.get('regexp', 0)

        if type(srch) != UnicodeType:
            srch = unicode(srch, 'utf-8')
        if type(rep) != UnicodeType:
            rep = unicode(rep, 'utf-8')

        def sr_std(text):
            """ standard search replace using the string module """
            found = 0

            if type(text) != UnicodeType:
                try:
                    text = unicode(text, 'utf-8')
                except:
                    try:
                        text = unicode(text, 'iso8859-15')
                    except:
                        import pdb, sys
                        e, m, tb = sys.exc_info()
                        pdb.post_mortem(tb)
            if text.find(srch) != -1:
                found = 1

            if search_only:
                ntext = text
            else:
                ntext = text.replace(srch, rep)

            return ntext.encode('utf-8'), found

        def sr_regexp(text):
            """ search and replace using regexp module """
            found = 0
            if type(text) != UnicodeType:
                try:
                    text = unicode(text, 'utf-8')
                except:
                    try:
                        text = unicode(text, 'iso8859-15')
                    except:
                        import pdb, sys
                        e, m, tb = sys.exc_info()
                        pdb.post_mortem(tb)
                        
            if re.findall(srch, text):
                found = 1

            if search_only:
                ntext = text
            else:
                ntext = re.sub(srch, rep, text)
            return ntext.encode('utf-8'), found

        METHOD = sr_std
        if regexp:
            METHOD = sr_regexp

        if PTYPE in ['Document', 'Topic Document', 'News Article', 'Event']:
            for l in object.get_languages():
                print "PTYPE IS:", PTYPE
                ntext = ntitle = ndescription = ''

                text = object.EditableBody(l)
                title = object.Title(l)
                description = object.Description(l)

                ntext, S = METHOD(text)
                STATE = STATE or S
                ntitle, S  = METHOD(title)
                STATE = STATE or S
                ndescription, S = METHOD(description)
                STATE = STATE or S
                if STATE:
                    if PTYPE=='Event':
                        object.manage_edit(text_format=object.text_format, text=ntext, title=ntitle, description=ndescription, language=l)
                    else:
                        object.manage_edit(text_format=object.text_format, text=ntext, title=ntitle, description=ndescription, localizer_language=l)
        elif PTYPE in ['FAQ Entry']:
            for l in object.get_languages():
                print "PTYPE IS:", PTYPE
                nquestion = ''
                ntitle = ''
                ndescription = ''
                nanswer = ''

                question = object.Question(l)
                title = object.Title(l)
                description = object.Description(l)
                answer = object.Answer(l)

                nquestion, S = METHOD(question)
                STATE = STATE or S
                ntitle, S  = METHOD(title)
                STATE = STATE or S
                ndescription, S = METHOD(description)
                STATE = STATE or S
                nanswer, S = METHOD(answer)
                STATE = STATE or S
                if STATE:
                    object.manage_edit(text_format=object.text_format, question=nquestion, answer=nanswer, title=ntitle, description=ndescription, localizer_language=l)
        
        elif PTYPE in ['Discussion Item', 'Discussion Article']:
            title = object.Title()
            description = object.Description()
            text = object.EditableBody()
            ntitle, S  = METHOD(title)
            STATE = STATE or S
            ndescription, S = METHOD(description)
            STATE = STATE or S
            ntext, S = METHOD(text)
            STATE = STATE or S
            if STATE:
                object.manage_edit(text_format=object.text_format, text=ntext, title=ntitle)
                object.setDescription(ndescription)

        elif PTYPE in ['File', 'Image']:
            title = object.Title()
            description = object.Description()
            ntitle, S  = METHOD(title)
            STATE = STATE or S
            ndescription, S = METHOD(description)
            STATE = STATE or S
            if STATE:
                object.setTitle(ntitle)
                object.setDescription(ndescription)

        elif PTYPE in ['OSH_Link', 'OSH_DBContent']:
            title = object.Title()
            description = object.getDescription()

            ntitle, S  = METHOD(title)
            STATE = STATE or S
            ndescription, S = METHOD(description)
            STATE = STATE or S
            if STATE:
                object.setTitle(ntitle)
                object.setDescription(ndescription)

        elif PTYPE in ['Topic', 'Folder', 'News Board', 'Calendar', 'FAQ Folder']:
            for l in object.get_languages():

                title = object.Title(l)
                description = object.Description(l)
                ntitle, S  = METHOD(title)
                STATE = STATE or S
                ndescription, S = METHOD(description)
                STATE = STATE or S
                if STATE:
                    object.manage_editFolder(title=ntitle, description=ndescription, localizer_language=l)

        elif PTYPE in ['PublicationFolder', 'Publication', 'PublicationFile']:
            title = object.getTitle()
            description = object.getDescription()

            ntitle, S  = METHOD(title)
            STATE = STATE or S
            ndescription, S = METHOD(description)
            STATE = STATE or S
            if STATE:
                object.setTitle(ntitle)
                object.setDescription(ndescription)

        elif PTYPE in ['Portlet']:
            for l in object.get_languages():
                print "PTYPE IS:", PTYPE
                ntext = ntitle = ndescription = ''

                text = object.getHtml_data(l)
                title = object.Title(l)
                description = object.Description(l)

                ntext, S = METHOD(text)
                STATE = STATE or S
                ntitle, S  = METHOD(title)
                STATE = STATE or S
                ndescription, S = METHOD(description)
                STATE = STATE or S
                if STATE:
                    object.setTitle(ntitle, l)
                    object.setDescription(ndescription, l)
                    object.setLocalProp('html_data', 'lines', l, ntext)
        return STATE

    def __init__(self, id=''):
        QCTransform.__init__(self)

def register():
    return SearchReplace()
