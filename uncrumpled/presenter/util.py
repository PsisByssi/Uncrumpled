from types import GeneratorType

system_base = {'binds': {},
              'bind_handlers': [],
              'functions': {},
              'ui_event_types': [],
              'pages': {},
              'profiles': []}

# The Responses we can handle from the core
# PRESENTER_CORE_API = ('bind_add', 'bind_remove')

# Requests the ui can handle # TODO generate from the GUI
UI_API = ('status_update',
          'bind_remove',
          'window_show',
          'window_hide',
          'welcome_screen',
          'page_load',
          'page_close',
          'system_hotkey_register',
          'system_hotkey_unregister',
          'profile_set_active',
          'page_settings_view')


# Event types the ui can handle #TODO Generate
UI_EVENT_TYPES = ('on_key_down', )


# TODO does this mean the dict should just map files to page_id ?
def page_id_from_file(pages, file):
    ''' returns page id or -1'''
    for page_id, values in pages.items():
        if file == values['file']:
            return page_id
    raise ValueError()



