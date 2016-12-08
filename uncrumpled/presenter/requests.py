
'''
    All the functions the UI uses to interact with the core.
'''

from uncrumpled.presenter.presenter import uncrumpled_request
from uncrumpled.core import requests as req

@uncrumpled_request
def book_create(app, profile, book, hotkey, active_profile, **kwargs):
    response = req.book_create(app,
                               profile=profile,
                               book=book,
                               hotkey=hotkey,
                               active_profile=active_profile,
                               **kwargs)
    return response

@uncrumpled_request
def cmdpane_search(app, query):
    response = req.cmdpane_search(app, query=query)
    return response

@uncrumpled_request
def cmdpane_item_open(app, item):
    response = req.cmdpane_item_open(app, item=item)
    return response

@uncrumpled_request
def profile_create(app, profile):
    response = req.profile_create(app, profile=profile)
    return response

@uncrumpled_request
def profile_delete(app, profile):
    response = req.profile_delete(app, profile=profile)
    return response


@uncrumpled_request
def profile_set_active(app, profile):
    response = req.profile_set_active(app, profile=profile)
    return response


@uncrumpled_request
def profile_get_active(app):
    response = req.profile_get_active(app)
    return response


@uncrumpled_request
def ui_init(app):
    response = req.ui_init(app, app.first_run)
    return response


@uncrumpled_request
def hotkey_pressed(app, profile, program, hotkey):
    system_page = app.SYSTEM['pages']
    response = req.hotkey_pressed(app, profile, program, hotkey, system_page)
    return response

def system_get(app):
    '''for debugging'''
    return ["system_gotten(system={})".format(app.SYSTEM)]
