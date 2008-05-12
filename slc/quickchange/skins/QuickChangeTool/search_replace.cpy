## Controller Python Script "search_replace"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=search_text='', replace_text=None, regexp=0, recursive=0
##title=Do a Search and Replace

request = context.REQUEST
mssg = ''
qct = context.portal_quickchangetool

if request.has_key('form.button.Search'):
    JOB = qct.setupSearchReplaceJob(path="/".join(context.getPhysicalPath()),
                                    search_text=search_text,
                                    replace_text=replace_text,
                                    regexp=regexp,
                                    recursive=recursive,
                                    search_only=1)

    log = JOB.getLogData()

    mssg = "Search done."
    return state.set(status='success', context=context, portal_status_message=mssg, logdata=log, search_text=search_text, replace_text=replace_text, recursive=recursive, regexp=regexp, mode="search")

elif request.has_key('form.button.Replace'):
    targets = request.get('targets', None)
    JOB = qct.setupSearchReplaceJob(path="/".join(context.getPhysicalPath()),
                                    search_text=search_text,
                                    replace_text=replace_text,
                                    targets=targets,
                                    regexp=regexp,
                                    recursive=recursive,
                                    search_only=0)

    log = JOB.getLogData()
    mssg = "Search & Replace succeeded."
    return state.set(status='success', context=context, portal_status_message=mssg, logdata=log, search_text=search_text, replace_text=replace_text, recursive=recursive, regexp=regexp, mode="replace")
else:
    mssg = "No valid action chosen"
    return state.set(status='failure', context=context, portal_status_message=mssg)


return state.set(status='success', context=context, portal_status_message=mssg)
