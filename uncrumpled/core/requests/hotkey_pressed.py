'''
    This module exposes hoyket_pressed
    It sends signals to load and close pages.
    It creates new pages if required,
'''
import os
import json

import halt

from uncrumpled.core import dbapi
from uncrumpled.core import core_request
from uncrumpled.core import responses as resp
from uncrumpled.core import requests as req

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


def page_find(db, profile, book, program):
    '''
    if a specific page exists, returns that,
    otherwise a general page if one exists
    '''
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


def no_process(core, profile, book, program, hotkey):
    '''
    What to do if a page doesn't exist.
    Very important part of uncrumpled. (very basic atm)

    First check if the book is set to load a loose page TODO
    then follow some sort of inheritance/composition rules...

    From old uncrumpled: (not sure if i want to change this)
        Order of importince of rules
            Program, Book Profile
            Program Rule, e.g if firefox always do this
            Book Profile Rule
            Default Rule
            So far only the Profile Book checked, and then Book
    '''
    cond = "WHERE Book == '{}' AND \
                  Profile == '{}'".format(book, profile)
    book_mash = json.loads(halt.load_column(core.db, 'Books',
                                           ('MashConfig',), cond)[0][0])
    no_process = book_mash['no_process']

    specific = None
    loose = None

    if no_process == 'read': # load
        raise NotImplementedError
    elif no_process == 'shelve': # do nothing
        return False
    elif no_process == 'loose': # todo delete this.. read should do this, loose 
        return book_mash['loose']

    # elif book_mash['no_process'] == 'prompt'
        # mmm how to do this now :)
        # if not gui_newbook.prompt_create(book,
                # active_program, self.active_profile):
            # return
        # else:
            # edb.create_page(book,
                            # active_program,
                            # self.active_profile)
    elif no_process == 'write': #new
        pass

    elif no_process == 'bookmark': #load specific
        raise NotImplementedError
        title = util.parse_title()
        specific = title

    for aresp in resp.noopify(req.page_create(core, profile, book, program,
                               specific, loose)):
        rowid = aresp['page_id']
        yield aresp
    return rowid


@core_request()
def hotkey_pressed(core, profile, program, hotkey, system_pages):
    '''
    profile -> active profile
    hotkey -> the pressed hotkey

    evaluates a hotkey, can either
    * load an existing page
    * create a page, (optionally load it)
    '''

    hotkey = json.dumps(hotkey)
    cond = "WHERE Hotkey == '{}' AND \
                  Profile == '{}'".format(hotkey, profile)
    book = halt.load_column(core.db, 'Hotkeys', ('Book',), cond)[0][0]

    page_id = page_find(core.db, profile, book, program)
    if not page_id:
        response = no_process(core, profile, book, program, hotkey)
        if response:
            aresp = next(response)
            yield aresp
            page_id = yield from response
            yield resp.resp('page_load', page_id=page_id)
        else:
            yield False
    else:
        if system_pages[page_id]['is_open']:
            yield resp.resp('page_close', page_id=page_id)
            yield resp.resp('window_hide')
        else:
            yield resp.resp('page_load', page_id=page_id)
