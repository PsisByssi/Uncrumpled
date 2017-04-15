
'''
    All the functions the UI uses to interact with the core.
'''

from uncrumpled.presenter.presenter import uncrumpled_request
from uncrumpled.presenter import util
from uncrumpled.core import core_request
from uncrumpled.core import requests as req
from uncrumpled.core import responses as core_resp

#TODO SHOULD return a dict of stuff so that these functions
# are ui or pluging/client agnostic

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


@uncrumpled_request
def page_settings_view(app, file):
    ''' Return settings for a page '''
    try:
        page_id = util.page_id_from_file(app.SYSTEM['pages'], file)
    except ValueError:
        return api_error('No file exists...', file=file)
    response = req.settings_from_pageid(app, page_id, req.SettingSelector.all)
    return response


@uncrumpled_request
def page_deactivate(app, file):
    '''When the user is no longer viewing our uncrumped page,
    The page might be backgrounded or the tab focus could have changed'''
    try:
        page_id = util.page_id_from_file(app.SYSTEM['pages'], file)
    except ValueError:
        return api_error('No file exists...', file=file)
    response = noop('page_close', page_id=page_id)
    return response


def system_get(app):
    '''for debugging'''
    from pprint import pprint as pp
    sys = app.SYSTEM
    import pdb;pdb.set_trace()
    # return ["system_gotten(system={})".format(app.SYSTEM)]


@core_request(is_resp_id=True)
def api_error(msg, **kwargs):
    yield core_resp.api_error(msg, **kwargs)

@core_request()
def noop(method, **kwargs):
    yield core_resp.noop(method, **kwargs)


