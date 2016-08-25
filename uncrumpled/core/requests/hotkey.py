
import logging

from uncrumpled.core import dbapi
from uncrumpled.core import core_request
from uncrumpled.core import responses as resp


@core_request(is_resp_id=True)
def hotkey_create(core, profile, book, hotkey):
    if dbapi.hotkey_create(core.db, profile, book, hotkey):
        yield resp.noop(key='hotkey_created')
    else:
        yield resp.noop(key='hotkey_taken')


@core_request(is_resp_id=True)
def hotkey_delete(core, profile, book, hotkey):
    if dbapi.hotkey_delete(core.db, profile, book, hotkey):
        yield resp.noop(key='hotkey_deleted')
    else:
        yield resp.noop(key='hotkey_not_found')


@core_request(is_resp_id=True)
def hotkey_update(core, profile, book, hotkey):
    if dbapi.hotkey_update(core.db, profile, book, hotkey):
        yield resp.noop(key='hotkey_updated')
    else:
        yield resp.noop(key='hotkey_not_found')


@core_request(is_resp_id=True)
def hotkeys_load(core, active_profile):
    '''
    only use this at startup, init system wide hotkeys for the active profile
    '''
    for hotkey in dbapi.hotkey_get_all(core.db, active_profile):
        yield resp.resp('system_hotkey_register', hotkey=hotkey)


@core_request(is_resp_id=True)
def hotkeys_reload(core, old, new):
    '''
    changes the active system hotkeys based on the profiles

    :old: old profile that has had it's hotkeys currently loaded
    :new: new profile
    '''
    if old != new:
        for hotkey in dbapi.hotkey_get_all(core.db, old):
            yield resp.resp('system_hotkey_unregister', hotkey=hotkey)
        for hotkey in dbapi.hotkey_get_all(core.db, new):
            yield resp.resp('system_hotkey_register', hotkey=hotkey)
