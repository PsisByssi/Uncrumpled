from uncrumpled.core import dbapi
from uncrumpled.core import core_request
from uncrumpled.core import responses as resp


@core_request(is_resp_id=True)
def profile_create(app, profile):
    if dbapi.profile_create(app.db, profile):
        yield resp.status(key='profile_created',
                           code=1,
                           template={'profile': profile})
    else:
        yield resp.status(key='profile_taken',
                           code=0,
                           template={'profile': profile})


@core_request(is_resp_id=True)
def profile_delete(app, profile):
    if dbapi.profile_delete(app.db, profile):
        yield resp.status(key='profile_deleted',
                           code=1,
                           template={'profile': profile})
    else:
        yield resp.status(key='profile_not_found',
                           code=0,
                           template={'profile': profile})


@core_request(is_resp_id=True)
def profile_get_active(app):
    dbapi.profile_get_active(app.db)
    yield resp.noop(key='profile_gotten')


@core_request(is_resp_id=True)
def profile_set_active(app, profile):
    dbapi.profile_set_active(app.db, profile)
    yield resp.status(key='profile_changed',
                       code=1,
                       template={'profile': profile})


