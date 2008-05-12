import re, Acquisition
import StringIO
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base, aq_parent, aq_inner
import os, re
from types import UnicodeType, StringType
from Products.Archetypes.public import RichWidget
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

TYPES = ['Document', 'RichDocument', 'News Item', 'Event']
SPECIALFISH = ['OSH_Link', 'Provider']


class SearchReplaceView(BrowserView):
    """ Doing Search and Replace on the current context """
    
    template = ViewPageTemplateFile('searchreplace.pt')
    
    def __init__(self, context, request):
        super(SearchReplaceView, self).__init__(context, request)
        self.request = request
        self.context = context
        self.changed = []
        self.search_text = None
        self.replace_text = None
        self.recursive = False
        self.regexp = False
        self.search_only = True
        self.path = None
        
    def __call__(self):
        self.request.set('disable_border', True)
        self.search_text = self.request.get('search_text','')
        self.replace_text = self.request.get('replace_text','')
        self.recursive = self.request.get('recursive','')
        self.regexp = self.request.get('regexp','')
        self.search_only = not self.request.get('form.button.Replace', False)

        self.path = "/".join(self.context.getPhysicalPath())

        if not self.search_only:
            self.do_replace()
            
        return self.template()



    def do_replace(self):
        """ starting in the root, working through all language paths """
        if not self.search_text: return
        context = Acquisition.aq_inner(self.context)
        portal_languages = getToolByName(context, 'portal_languages')
        langs = portal_languages.getSupportedLanguages()
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        portal_catalog = getToolByName(context, 'portal_catalog')
        portal_path = "/".join(portal.getPhysicalPath())
        out = StringIO.StringIO()

        SR = SearchReplace()

        #oshold  = dict(search=OLDOSH, replace=OLDOSHREP, regexp=0)
        #oldeu  = dict(search=OLDEU, replace=OLDEUREP, regexp=0)
        #oldag  = dict(search=OLDAG, replace=OLDAGREP, regexp=0)
        #oshparms = dict(search=OSHPrefix, replace=OSHREP, regexp=1)

#        for lang in langs:
#            base = getattr(portal, lang, None)
#            if base is None:
#                continue
#            params = dict(search=PAT%lang, replace=REP%lang, regexp=1)
#
#            path = '%s/%s' % (portal_path, lang)
#            results = portal_catalog(path=path, portal_type=TYPES)
#            for result in results:
#                ob = result.getObject()
#                STATE = False
#
#                S = SR.apply(ob, oshold)
#                STATE = STATE or S
#
#                if STATE:
#                    print "Object %s has been fixed" % result.getURL()

        if self.recursive:
            results = portal_catalog(Languge='all', path=self.path) # TODO, make language tree support
        else:
            results = [context]

        params = dict(search=self.search_text, replace=self.replace_text, regexp=self.regexp)
        self.changed = []

        for result in results:
            if hasattr(Acquisition.aq_base(result), 'getObject'):
                ob = result.getObject()
            else:
                ob = result
                
            STATE = False

            S = SR.apply(ob, params)
            STATE = STATE or S

            if STATE:
                obpath = "/".join(ob.getPhysicalPath())
                oburl = ob.absolute_url()
                self.changed.append(oburl)
                print "Object %s has been fixed" % obpath



def _getRichTextFields(object):
    return [f for f in object.Schema().fields()
              if isinstance(f.widget, RichWidget)]



OLDOSH = 'osha.eu.int'
OLDOSHREP = 'osha.europa.eu'

OSHPrefix = 'href="http://osha.europa.eu/(.*?)"'
OSHREP = 'href="/\\1"'

OLDOSH = 'osha.eu.int'
OLDOSHREP = 'osha.europa.eu'

OLDEU = 'europe.osha.europa.eu'
OLDEUREP = 'osha.europa.eu'

OLDAG = 'agency.osha.europa.eu'
OLDAGREP = 'osha.europa.eu'


PAT = 'href="/(?!%s)(.*)"'
REP = 'href="/%s/\\1"'



    
class SearchReplace:
    """ The Search & Replace Transforms can search for a given string and replace it by another string. 
    The Matching is literal and does not use regular expressions
    """
    def apply(self, object, params={}):
        """ apply a Search & Replace on the content of an object """
        STATE = 0 
        # Describes if a pattern has been found in this object. 
        # If it has been found it'll also be replaced, so we can use this for both search and replace mode.
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

        print "S&R portal_type:", PTYPE
        
        if PTYPE in ['Document', 'RichDocument', 'News Item', 'Event']:
            ntext = ntitle = ndescription = ''
            fields = _getRichTextFields(object)
            STATE = False
            
            for field in fields:
                text = field.getRaw(object)
                ntext, S = METHOD(text)
                STATE = STATE or S
                if S:
                    field.set(object, ntext)
                
            title = object.Title()
            ntitle, S  = METHOD(title)
            STATE = STATE or S
            if S:
                object.setTitle(ntitle)
                
            description = object.Description()            
            ndescription, S = METHOD(description)
            STATE = STATE or S
            if S:
                object.setDescription(ndescription)

            return STATE
        
        elif PTYPE in ['OSH_Link', 'Provider']:
            ntext = ntitle  = ''
            fields = _getRichTextFields(object)
            STATE = False
            
            for field in fields:
                text = field.getRaw(object)
                ntext, S = METHOD(text)
                STATE = STATE or S
                if S:
                    field.set(object, ntext)
                
            title = object.Title()
            ntitle, S  = METHOD(title)
            STATE = STATE or S
            if S:
                object.setTitle(ntitle)
                
            url = object.getRemoteUrl()
            # fix to make the other re match
            url = 'href="%s"' % url
            nurl, S  = METHOD(url)
            STATE = STATE or S
            if S:
                nurl = nurl.replace('href="', '')
                if nurl[-1]=='"': nurl = nurl[:-1]
                object.setRemoteUrl(nurl)

            return STATE            

        