
'''
    All the functions the UI uses to interact with the core.
'''
# TODO passing in core class should be removed

from uncrumpled.presenter.presenter import uncrumpled_request
from uncrumpled.core import requests as req


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
