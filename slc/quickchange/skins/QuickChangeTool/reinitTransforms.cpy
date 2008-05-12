## Controller Python Script 'reinitTransforms'
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##bind state=state
##parameters=
##title=Reinitialize Transforms
##


result = context.initializeTransforms()

state.set(portal_status_message='Transforms reinitialized')
if state.getStatus() != 'success':
    state.set(portal_status_message='Please fix your errors')

return state