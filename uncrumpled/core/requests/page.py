'''

from uncrumpled.core.util import resp_status, resp_noop
def page_create(db, profile, book, program, specific):
    if type(program) not in (list, tuple):
        return resp_progerr('programmer error',
                            'msg', 'param "program" must bet a list or tuple'):

book_create
profile_create


we also need: (active, program, note_state)
handle_hotkey(pressedkey, program, book, profile)
    -> loads pages
    -> creates pages
    -> alert boxes
    -> reload hotkeys
    -> gui_load_window(heaps of data sent here)
    -> update status bar


DATABASE_FILE = 'unc.db'
NOTES = {}
REGISTERED_HL = {}

# def cmdpane_search

# def cmdpane_


# def resp_alert(msg, code):

# def get_config
    # side effects:
'''
