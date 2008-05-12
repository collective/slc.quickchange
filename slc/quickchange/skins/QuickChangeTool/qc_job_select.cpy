## Controller Python Script 'qc_job_select'
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##bind state=state
##parameters=select_by, selector_script=''
##title=Write the selection method
##

if select_by == 'script':
    if selector_script.strip() == '':
        return state.set(status='failure', context=context, portal_status_message='If you choose script, you need to select one. Try again.')
    context.setSelectScript(selector_script)
    context.setSelectType(select_by)
elif select_by == 'manual':
    context.setSelectType(select_by)
elif select_by == 'criteria':
    context.setSelectType(select_by)
else:
    return state.set(status='failure', context=context, portal_status_message='Invalid type given. Try again.')

state.set(portal_status_message='')
if state.getStatus() != 'success':
    state.set(portal_status_message='Please try again.')

return state
