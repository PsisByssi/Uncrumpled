
import logging

from uncrumpled.core import dbapi
from uncrumpled.core import responses as resp


def hotkey_create(core, profile, book, hotkey):
    if dbapi.hotkey_create(core.db, profile, book, hotkey):
        return resp.noop(key='hotkey_created')
    else:
        return resp.noop(key='hotkey_taken')


def hotkey_delete(core, profile, book, hotkey):
    if dbapi.hotkey_delete(core.db, profile, book, hotkey):
        return resp.noop(key='hotkey_deleted')
    else:
        return resp.noop(key='hotkey_not_found')


def hotkey_update(core, profile, book, hotkey):
    if dbapi.hotkey_update(core.db, profile, book, hotkey):
        return resp.noop(key='hotkey_updated')
    else:
        return resp.noop(key='hotkey_not_found')


def hotkeys_load(core):
    '''
    only use this at startup, init system wide hotkeys for the active profile
    '''
    active_profile = dbapi.profile_get_active(core.db)
    if not active_profile:
        raise Exception('Somehow...: No Active Profile Found')
    rv = []
    for hotkey in dbapi.hotkey_get_all(core.db, active_profile):
        rv.append(resp.noop(key='hotkey_register', hotkey=hotkey))
    logging.info('No Hotkeys Detected, no Listening going on')
    if rv:
        return True


def hotkeys_reload(core, old, new):
    '''
    :old: old profile, must have already been activated
    :new: new profile
    changes the active system hotkeys based on the profiles
    '''
    if old != new:
        rv = []
        for hotkey in dbapi.hotkey_get_all(core.db, old):
            logging.info('Unregister ' + str(hotkey))
            rv.append(resp.noop(key='system_hotkey_unregister', hotkey=hotkey))
        for hotkey in dbapi.hotkeys_get_all(core.db, new):
            logging.info('register' + str(hotkey))
            rv.append(resp.noop(key='system_hotkey_register', hotkey=hotkey))
        if rv:
            return True

