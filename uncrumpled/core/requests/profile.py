from uncrumpled.core import dbapi
from uncrumpled.core import core_request
from uncrumpled.core import responses as resp


@core_request(is_resp_id=True)
def profile_create(core, profile):
    if dbapi.profile_create(core.db, profile):
        yield resp.status(key='profile_created',
                           code=1,
                           template={'profile': profile})
    else:
        yield resp.status(key='profile_taken',
                           code=0,
                           template={'profile': profile})


@core_request(is_resp_id=True)
def profile_delete(core, profile):
    if dbapi.profile_delete(core.db, profile):
        yield resp.status(key='profile_deleted',
                           code=1,
                           template={'profile': profile})
    else:
        yield resp.status(key='profile_not_found',
                           code=0,
                           template={'profile': profile})


@core_request(is_resp_id=True)
def profile_get_active(core):
    dbapi.profile_get_active(core.db)
    yield resp.noop(key='profile_gotten')


@core_request(is_resp_id=True)
def profile_set_active(core, profile):
    dbapi.profile_set_active(core.db, profile)
    yield resp.status(key='profile_changed',
                       code=1,
                       template={'profile': profile})


