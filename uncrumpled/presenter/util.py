from types import GeneratorType

system_base = {'binds': {},
              'bind_handlers': [],
              'functions': {},
              'ui_event_types': [],
              'pages': {},
              'profiles': []}

# The Responses we can handle from the core
# PRESENTER_CORE_API = ('bind_add', 'bind_remove')

# Requests the ui can handle # TODO move to the gui
UI_API = ('status_update',
          'bind_remove',
          'show_window',
          'welcome_screen',
          'page_load',
          'page_close',
          'system_hotkey_register',
          'system_hotkey_unregister',
          'profile_set_active')


def make_class_name(string):
    '''given foo_bar returns FooBar'''
    parts = string.split('_')
    return ''.join(x.capitalize() for x in parts)


def traverse(o, tree_types=(list, tuple, GeneratorType)):
    if isinstance(o, tree_types):
        for value in o:
            for subvalue in traverse(value, tree_types):
                yield subvalue
    else:
        yield o
