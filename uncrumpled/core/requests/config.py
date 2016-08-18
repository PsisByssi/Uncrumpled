
import logging

from uncrumpled.core import responses as resp
from uncrumpled.core import requests as req
from uncrumpled.core import dbapi
# from uncrumpled.core.profile import load_hotkeys


def ui_init(core, user_or_token=None, password=None):
    '''
    Code for startup
    '''
    logging.info('first time ?-> :' + str(core.first_run))
    if core.first_run:
        yield resp.resp('show_window')
        yield resp.resp('welcome_screen')
    # if data.get('new_user'):
        # yield config.new_user(data)
    # yield config.ui_config()
    profile = dbapi.profile_get_active(core.db)
    dbapi.profile_set_active(core.db, profile)
    yield resp.noop('profile_set_active', profile=profile)
    for aresp in req.hotkeys_load(core, profile):
        yield aresp
