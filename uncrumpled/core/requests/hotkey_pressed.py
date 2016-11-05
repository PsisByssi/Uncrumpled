'''
    This module exposes hoykey_pressed
    It sends signals to load and close pages.
    It creates new pages if required,

    REFACTOR IDEAS:
        One idea would be to make the no_process options:
            Read, Write, Shelve etc
        be retrieved after getting the book, then dispatching the
        page_find, and no_process calls to them.

        should then be easier to follow what happens on a type of
        keypress

        the goal is to make it simple and concise for other people
        to read and understand, (group conditionals that are related)

'''
import os
import json

import halt

from uncrumpled.core import dbapi
from uncrumpled.core import core_request
from uncrumpled.core import responses as resp
from uncrumpled.core import requests as req
from uncrumpled.core import util

DEVELOPING = False

def page_specific_match(current, page):
    pass


def page_itr(db, profile, book, program):
    '''
    the active profie, program, and the book to which the
    hotkey belongs are required.

    :return: rowid, specific
    '''
    cond = "WHERE Profile == '{}' AND \
                  Book == '{}' AND \
                  Program == '{}'".format(profile, book, program)

    results = halt.load_column(db, 'Pages', ('Id', 'Specific',), cond)
    for x in results:
        yield x


def page_find(db, profile, book, program, bookopts):
    '''
    if a specific page exists, returns that,
    otherwise a general page if one exists
    '''
    #TODO del
    global DEVELOPING
    if DEVELOPING and program in ('python3', 'python'):
        program = 'uncrumpled'

    if bookopts['no_process'] == 'read':
        return

    general = False
    for rowid, specific in page_itr(db, profile, book, program):
        if specific == dbapi.UNIQUE_NULL:
            general = rowid
            continue
        # specific = page_specific_match(current, page) # todo move io out?
        # if page[1]:
            # return specific
    else:
        if general:
            return general


def no_process(app, profile, book, program, hotkey, bookopts):
    '''
    What to do if a page doesn't exist.
    Very important part of uncrumpled. (very basic atm)

    returns False if nothing is to be done
    '''
    # First check if the book is set to load a loose page TODO
    # then follow some sort of inheritance/composition rules...

    # From old uncrumpled: (not sure if i want to change this)
        # Order of importince of rules
            # Program, Book Profile
            # Program Rule, e.g if firefox always do this
            # Book Profile Rule
            # Default Rule
            # So far only the Profile Book checked, and then Book
    no_process = bookopts['no_process']

    specific = None
    loose = None

    # Load a page
    if no_process == 'read':
        # If we got this far, no page has been set for reading
        assert not bookopts.get('read_page')
        no_read_file = bookopts.get('no_read_file')

        # create a loose page with a random name
        if no_read_file == 'create_with_random_name':
            loose = util._rand_name_in_list(dbapi.loose_get_all(app.db, profile))
            for aresp in resp.noopify(req.page_create(app, profile, book, program,
                                       specific, loose)):
                rowid = aresp.get('page_id')
                assert rowid
                yield aresp
            # Point the book to the page
            dbapi.book_update(app.db, book, profile, read_page=rowid)
            return rowid
        else:
            raise NotImplementedError

    # Do nothing
    elif no_process == 'shelve':
        return False

    # elif book_mash['no_process'] == 'prompt'
        # mmm how to do this now :)
        # if not gui_newbook.prompt_create(book,
                # active_program, self.active_profile):
            # return
        # else:
            # edb.create_page(book,
                            # active_program,
                            # self.active_profile)
    # Create New Page
    elif no_process == 'write':
        for aresp in resp.noopify(req.page_create(app, profile, book, program,
                                   specific, loose)):
            rowid = aresp.get('page_id')
            assert rowid
            yield aresp
        return rowid

    # Load specific
    elif no_process == 'bookmark':
        raise NotImplementedError
        title = util.parse_title()
        specific = title


@core_request()
def hotkey_pressed(app, profile, program, hotkey, system_pages):
    '''
    profile -> active profile
    hotkey -> the pressed hotkey

    evaluates a hotkey, can either
    * load an existing page
    * create a page, (optionally load it)
    '''
    # TODO DELETE
    global DEVELOPING
    if hasattr(app, 'DEVELOPING'):
        DEVELOPING = app.DEVELOPING

    # Find the book that is bound to the hotkey
    hotkey = json.dumps(hotkey)
    cond = "WHERE Hotkey == '{}' AND \
                  Profile == '{}'".format(hotkey, profile)
    book = halt.load_column(app.db, 'Hotkeys', ('Book',), cond)[0][0]

    cond = "WHERE Book == '{}' AND \
                  Profile == '{}'".format(book, profile)
    bookopts = json.loads(halt.load_column(app.db, 'Books',
                                           ('MashConfig',), cond)[0][0])

    if bookopts['no_process'] == 'read':
        page_id = bookopts.get('read_page')
    else:
        page_id = page_find(app.db, profile, book, program, bookopts)

    # Potentially create and load a new page
    if not page_id:
        response = no_process(app, profile, book, program, hotkey, bookopts)
        if response:
            create_resp = next(response)
            yield create_resp
            page_id = yield from response
            yield resp.resp('page_load', page_id=page_id)
            yield resp.resp('window_show')
        else:
            yield False
    # Open or close a page
    else:
        if system_pages[page_id]['is_open']:
            yield resp.resp('page_close', page_id=page_id)
            yield resp.resp('window_hide')
        else:
            # NOTE, this is a simple work around to make uncrumpled
            # be able to have notepages on it, This implementaiton limits
            # alot of options (we are not using them atm so it is ok)
            for page, value in system_pages.items():
                if page != page_id:
                    yield resp.resp('page_close', page_id=page)
            yield resp.resp('page_load', page_id=page_id)
            yield resp.resp('window_show')
