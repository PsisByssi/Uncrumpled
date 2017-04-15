'''
 provides functions for saveing and viewing settings
 for a given page
'''
from enum import Enum

from uncrumpled.core import dbapi
from uncrumpled.core.core import core_request
from uncrumpled.core import responses as resp


class SettingSelector(Enum):
    all = 0
    page = 10
    page_and_book = 11
    page_and_profile = 12
    book = 20
    book_and_profile = 21
    profile = 30


@core_request(is_resp_id=False)
def settings_from_pageid(app, page_id, level: SettingSelector):
    data = {}
    page_settings = dbapi.page_get(app.db, page_id)
    if page_settings:
        data['page_settings'] = page_settings
    else:
        yield resp.status(key='page_not_found', code=0)
        return

    # Get the profile settings
    profile = page_settings.get('Profile')
    if level in (SettingSelector.all,
                 SettingSelector.profile,
                 SettingSelector.book_and_profile,
                 SettingSelector.page_and_profile):
        profile_settings = dbapi.profile_get(app.db, profile)
        if profile_settings:
            data['profile_settings'] = profile_settings
        else:
            yield resp.status(key='profile_not_found',
                              code=0,
                              template={'profile': profile})
            return

    # Get the Book settings
    book = page_settings.get('Book')
    if level in (SettingSelector.all,
                 SettingSelector.book,
                 SettingSelector.book_and_profile,
                 SettingSelector.page_and_book):
        book_settings = dbapi.book_get(app.db, profile, book)
        if book_settings:
            data['book_settings'] = book_settings
        else:
            yield resp.status(key='book_not_found',
                              code=0,
                              template={'book': book})
            return

    yield resp.resp('page_settings_view', settings=data)

# TODO THE UPDATE SHOULD DELETE KEYS THAT ARE NO LONGER PRESENT!

@core_request(is_resp_id=True)
def settings_update(app, page_id, data):
    if not data:
        yield resp.api_error('Data required for an update')
        return

    for key in data:
        assert key in ('page_settings', 'book_settings', 'profile_settings')

    page = dbapi.page_get(app.db, page_id)

    page_settings = data.get('page_settings')
    if page_settings:
        if not dbapi.page_update_from_id(app.db, page_id, page_settings):
            yield resp.api_error('Page not found')
            return

    book_settings = data.get('book_settings')
    if book_settings:
        if not dbapi.book_update(app.db,
                                 page['book'],
                                 page['profile'],
                                 book_settings):
            yield resp.api_error('Book not found')
            return

    profile_settings = data.get('profile_settings')
    if profile_settings:
        if not dbapi.profile_update(app.db, page['profile'], profile_settings):
            yield resp.api_error('Profile not found')
            return


# @core_request(is_resp_id=True)
# def settings_file_update():

# def _validate_settings():

# def error():



