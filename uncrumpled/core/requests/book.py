from uncrumpled.core import dbapi
from uncrumpled.core.core import core_request
from uncrumpled.core import responses as resp
from uncrumpled.core import requests as req


# TODO yield request to make the book....
@core_request(is_resp_id=True)
def book_create(app, profile, book, hotkey, active_profile, **kwargs):
    try:
        dbapi.book_create(app.db, profile, book, hotkey, **kwargs)
    except dbapi.UniqueNameError:
        yield resp.status(key='book_taken', code=0)
    except dbapi.UniqueHotkeyError:
        yield resp.status(key='hotkey_taken', code=0)
    except dbapi.NoHotkeyError:
        yield resp.status(key='hotkey_missing', code=0)
    else:
        if profile == active_profile:
            for aresp in req.hotkeys_reload(app, active_profile, profile):
                yield aresp
        yield resp.status(key='book_created', code=1, template={'book': book})


@core_request(is_resp_id=True)
def book_delete(app, book, profile):
    if dbapi.book_delete(app.db, book, profile):
        # Close any open windows # TODO
        yield resp.status(key='book_deleted', code=1, template={'book':book})
    else:
        yield resp.status(key='book_not_found', code=0, template={'book':book})


