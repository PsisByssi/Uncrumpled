
import logging

from uncrumpled.core import dbapi
from uncrumpled.core import responses as resp


def hotkey_create(core, profile, book, hotkey):
    if dbapi.hotkey_create(core.db, profile, book, hotkey):
        yield resp.noop(key='hotkey_created')
    else:
        yield resp.noop(key='hotkey_taken')


def hotkey_delete(core, profile, book, hotkey):
    if dbapi.hotkey_delete(core.db, profile, book, hotkey):
        yield resp.noop(key='hotkey_deleted')
    else:
        yield resp.noop(key='hotkey_not_found')


def hotkey_update(core, profile, book, hotkey):
    if dbapi.hotkey_update(core.db, profile, book, hotkey):
        yield resp.noop(key='hotkey_updated')
    else:
        yield resp.noop(key='hotkey_not_found')


def hotkeys_load(core, active_profile):
    '''
    only use this at startup, init system wide hotkeys for the active profile
    '''
    for hotkey in dbapi.hotkey_get_all(core.db, active_profile):
        yield resp.noop(key='system_hotkey_register', hotkey=hotkey)


def hotkeys_reload(core, old, new):
    '''
    changes the active system hotkeys based on the profiles

    :old: old profile that has had it's hotkeys currently loaded
    :new: new profile
    '''
    if old != new:
        for hotkey in dbapi.hotkey_get_all(core.db, old):
            yield resp.noop(key='system_hotkey_unregister', hotkey=hotkey)
        for hotkey in dbapi.hotkey_get_all(core.db, new):
            yield resp.noop(key='system_hotkey_register', hotkey=hotkey)
