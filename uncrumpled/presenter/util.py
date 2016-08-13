
system_base = {'binds': {},
              'bind_handlers': [],
              'functions': {},
              'ui_event_types': [],
              'profiles': []}

# The Responses we can handle from the core
# PRESENTER_CORE_API = ('bind_add', 'bind_remove')

# Requests the ui can handle # TODO move to the gui
UI_API = ('status_update', 'bind_remove')

def make_class_name(string):
    '''given foo_bar returns FooBar'''
    parts = string.split('_')
    return ''.join(x.capitalize() for x in parts)
