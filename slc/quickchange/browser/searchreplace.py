import re, Acquisition
import StringIO
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base, aq_parent, aq_inner
import os, re
from types import UnicodeType, StringType
from Products.Archetypes.public import RichWidget
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.AdvancedQuery import And, Or, In, Eq


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
        self.re_I = self.request.get('re_I', '')
        self.re_S = self.request.get('re_S', '')
        self.search_only = not self.request.get('form.button.Replace', False)
        self.alllangs = not not self.request.get('alllangs', None)
        
        self.path = "/".join(self.context.getPhysicalPath())

#        if not self.search_only:
        # always call do_replace, because the search_only parameter is now considered there
        self.do_replace()
        
        if len(self.changed):
            if self.search_only:
                message = u"The following objects would be found by your query (see below)"
            else:
                message = u"The following objects were fixed according to your query (see below)"
            getToolByName(self.context, 'plone_utils').addPortalMessage(message)
        return self.template()



    def do_replace(self):
        """ starting in the root, working through all language paths """
        if not self.search_text: 
            return
        context = Acquisition.aq_inner(self.context)
        portal_languages = getToolByName(context, 'portal_languages')
        langs = portal_languages.getSupportedLanguages()
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        portal_catalog = getToolByName(context, 'portal_catalog')
        if hasattr(portal_catalog, 'getZCatalog'):
            portal_catalog = portal_catalog.getZCatalog()        
        portal_path = "/".join(portal.getPhysicalPath())
        out = StringIO.StringIO()

        SR = SearchReplace()

        query = Or()
        queries = []
        # Recursive means: do a catalog query, based on paths
        # If translations have different ids, they won't be found this way.
        if self.recursive:
            if self.alllangs:
                # locate the language component in the path, if we have one. 
                # If there is one, it is exactly below the portal path
                pathelems = self.path.split("/")
                langidx = len(portal.getPhysicalPath())
                if len(pathelems)>= langidx and len(pathelems[langidx]) == 2 and pathelems[langidx] in langs:
                    # we have a language branch
                    relpathelems = pathelems[langidx+1:]
                    langpaths = []
                    for lang in langs:
                        langpath = "%s/%s/%s" %(portal_path, lang, "/".join(relpathelems))
                        langpaths.append(langpath)
                    query = In('path', langpaths) 
                else:
                    # no language branch, use the current path
                    query = Eq('path', self.path)
            else:
                query = Eq('path', self.path)
#            print str(query)
            results = portal_catalog.evalAdvancedQuery(query)
        else:
            # A non-recursive search for all language version uses LinguaPlone's getTranslation.
            # Here we are independent of paths / ids.
            # Of course this will fail if a translation reference is missing.
            if self.alllangs:
                results = list()
                for lang in langs:
                    trans = context.getTranslation(lang)
                    if trans:
                        results.append(trans)
            else:
                results = [context]

        params = dict(search=self.search_text, 
            replace=self.replace_text, 
            regexp=self.regexp,
            re_I=self.re_I,
            re_S=self.re_S,
            search_only=self.search_only)
        self.changed = []

        for result in results:
            if hasattr(Acquisition.aq_base(result), 'getObject'):
                try:
                    ob = result.getObject()
                except AttributeError, ae:
                    print "Error retrieving Object for %s" % result.getPath()
                    continue
            else:
                ob = result
                
            STATE = False

            S = SR.apply(ob, params)
            STATE = STATE or S

            if STATE:
                obpath = "/".join(ob.getPhysicalPath())
                oburl = ob.absolute_url()
                self.changed.append(oburl)
#                print "Object %s has been fixed" % obpath



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
            flags = None
            if params.get('re_I', ''):
                flags = re.I
            if params.get('re_S', ''):
                if flags:
                    flags = flags | re.S
                else:
                    flags = re.S
            patt = re.compile(srch, flags)
            if re.findall(patt, text):
                found = 1

            if search_only:
                ntext = text
            else:
                ntext = re.sub(patt, rep, text)
            return ntext.encode('utf-8'), found

        METHOD = sr_std
        if regexp:
            METHOD = sr_regexp

        #print "S&R portal_type:", PTYPE
        
        if PTYPE in ['Document', 'RichDocument', 'News Item', 'Event', 'Topic']:
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

        if PTYPE in ['Folder', 'Large Plone Folder', 'File']:
            STATE = False
            ntitle = ndescription = ''

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

        