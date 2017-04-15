
from uncrumpled.core.responses import _UI
from uncrumpled.presenter.util import UI_EVENT_TYPES

def get_functions():
    '''
    return all functions avaliable in the plugin system
    currently we have NO plugin system.
    '''
    return _UI

def get_event_types():
    return UI_EVENT_TYPES

