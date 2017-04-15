from uncrumpled.core import dbapi
from uncrumpled.core import core_request
from uncrumpled.core import responses as resp


@core_request(is_resp_id=True)
def page_create(app, profile, book, program, specific=None, loose=None,
                init_text=None):
    id = dbapi.page_create(app.db, profile, book, program, specific, loose)
    if id:
        yield resp.status(key='page_created', code=1, page_id=id,
                          init_text=init_text)
    else:
        id = dbapi.page_rowid_get(app.db, profile, book, program, specific,
                                  loose)
        yield resp.status(key='page_taken', code=0, page_id=id)


@core_request(is_resp_id=True)
def page_update(app, profile, book, program, specific=None, loose=None):
    if dbapi.page_update(app.db, profile, book, program, specific, loose):
        yield resp.status(key='page_updated', code=1)
    else:
        yield resp.status(key='page_not_found', code=0)


@core_request(is_resp_id=True)
def page_update_from_id(app, page_id, data):
    if dbapi.page_update_from_id(app.db, page_id, data):
        yield resp.status(key='page_updated', code=1)
    else:
        yield resp.status(key='page_not_found', code=0)


@core_request(is_resp_id=True)
def page_delete(app, profile, book, program, specific=None, loose=None):
    if dbapi.page_delete(app.db, profile, book, program, specific, loose):
        yield resp.status(key='page_deleted', code=1)
    else:
        yield resp.status(key='page_not_found', code=0)
