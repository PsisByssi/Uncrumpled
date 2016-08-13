
from uncrumpled.core import dbapi
from uncrumpled.core import responses as resp


def profile_create(core, profile):
    if dbapi.profile_create(core.db, profile):
        return resp.status(key='profile_created',
                           code=1,
                           template={'profile': profile})
    else:
        return resp.status(key='profile_taken',
                           code=0,
                           template={'profile': profile})


def profile_delete(core, profile):
    if dbapi.profile_delete(core.db, profile):
        return resp.status(key='profile_deleted',
                           code=1,
                           template={'profile': profile})
    else:
        return resp.status(key='profile_not_found',
                           code=0,
                           template={'profile': profile})


def profile_set_active(core, profile):
    return resp.status(key='profile_changed',
                       code=1,
                       template={'profile': profile})


def profile_get_active(core, profile):
    return resp.noop(key='profile_gotten',
                     data={'profile': profile})
