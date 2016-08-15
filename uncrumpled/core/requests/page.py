
from uncrumpled.core import dbapi
from uncrumpled.core import responses as resp

def page_create(core, profile, book, program, specific):
    '''create or update an uncrumpled page'''
    dbapi.page_create(core.db, profile, book, program, specific)

def page_update(core, profile, book, program, specific):
    dbapi.page_update(core.db, profile, book, program, specific)



# we also need: (active, program, note_state)
# handle_hotkey(pressedkey, program, book, profile)
    # -> loads pages
    # -> creates pages
    # -> alert boxes
    # -> reload hotkeys
    # -> gui_load_window(heaps of data sent here)


# DATABASE_FILE = 'unc.db'
# NOTES = {}
# REGISTERED_HL = {}

# def cmdpane_search

# def cmdpane_


# def resp_alert(msg, code):

# def get_config
    # side effects:
'''
