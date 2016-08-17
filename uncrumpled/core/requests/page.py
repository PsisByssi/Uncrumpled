
from uncrumpled.core import dbapi
from uncrumpled.core import responses as resp

def page_create(core, profile, book, program, specific=None, loose=None):
    if dbapi.page_create(core.db, profile, book, program, specific, loose):
        return resp.status(key='page_created', code=1)
    else:
        return resp.status(key='page_taken', code=0)

def page_update(core, profile, book, program, specific=None, loose=None):
    if dbapi.page_update(core.db, profile, book, program, specific, loose):
        return resp.status(key='page_updated', code=1)
    else:
        return resp.status(key='page_not_found', code=0)

def page_delete(core, profile, book, program, specific=None, loose=None):
    if dbapi.page_delete(core.db, profile, book, program, specific, loose):
        return resp.status(key='page_deleted', code=1)
    else:
        return resp.status(key='page_not_found', code=0)
