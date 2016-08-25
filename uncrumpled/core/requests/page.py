from uncrumpled.core import dbapi
from uncrumpled.core import core_request
from uncrumpled.core import responses as resp


@core_request(is_resp_id=True)
def page_create(core, profile, book, program, specific=None, loose=None,
                init_text=None):
    id = dbapi.page_create(core.db, profile, book, program, specific, loose)
    if id:
        yield resp.status(key='page_created', code=1, page_id=id,
                          init_text=init_text)
    else:
        yield resp.status(key='page_taken', code=0)


@core_request(is_resp_id=True)
def page_update(core, profile, book, program, specific=None, loose=None):
    if dbapi.page_update(core.db, profile, book, program, specific, loose):
        yield resp.status(key='page_updated', code=1)
    else:
        yield resp.status(key='page_not_found', code=0)


@core_request(is_resp_id=True)
def page_delete(core, profile, book, program, specific=None, loose=None):
    if dbapi.page_delete(core.db, profile, book, program, specific, loose):
        yield resp.status(key='page_deleted', code=1)
    else:
        yield resp.status(key='page_not_found', code=0)
