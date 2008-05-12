## Controller Python Script "topic_criteria"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=field=None, criterion_type=None, criteria=[], criterion_ids=None, acquireCriteria='', criteriatouse='', query='', joinResults=''
##title=Edit Criteria of a Topic

request = context.REQUEST
mssg = 'Your Changes have been saved.'
            
if request.has_key('form.button.Add'):
    context.addCriterion(field=field, criterion_type=criterion_type)

    mssg = 'New Criteria added.'
    
elif request.has_key('form.button.Save'):

    for rec in criteria:
        crit = context.getCriterion(rec.id)
        command = {}
        
        for attr in crit.editableAttributes():
            tmp = getattr(rec, attr, None)
            
            # Due to having multiple radio buttons on the same page
            # with the same name but belonging to different records,
            # they needed to be associated with different records with ids
            
            if tmp is None:
                tmp = getattr(rec, '%s__%s' % (attr, rec.id), None)
            
            command[attr] = tmp
        
        crit.apply(command)
        
    mssg= 'Changes to criteria saved.'

elif request.has_key('form.button.Delete'):

    if criterion_ids=='' or criterion_ids==None:
        mssg = 'No criteria selected for deletion'
        return state.set(status='failure', context=context, portal_status_message=mssg)

    else:
        for cid in criterion_ids:
            context.deleteCriterion(cid)
    
        mssg = 'Criteria deleted.'
        
elif request.has_key('form.button.Batch'):        
    bs = request.get('list_batchsize', '')
    if bs:
        context.setList_batchsize(bs)   

elif request.has_key('form.button.CriteriaToUse'):

    error = context.editQuery(criteriatouse, query, request)

    if error:
        mssg = error
        return state.set(status='failure', context=context, portal_status_message=mssg)


elif request.has_key('form.button.Join'):

    error = context.editJoinResults(joinResults=joinResults)

    if error:
        mssg = 'Could not change join-setting'
        return state.set(status='failure', context=context, portal_status_message=mssg)

    error = context.editAcquireCriteria(acquireCriteria)
    if error:
        mssg = 'Could not change criteria inheritance'
        return state.set(status='failure', context=context, portal_status_message=mssg)        

return state.set(status='success', context=context, portal_status_message=mssg)
