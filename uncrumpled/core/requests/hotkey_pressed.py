'''
    This module exposes only one function,  hoyket_pressed
    needs alot of helpers..
'''

import json
import logging

import halt

from uncrumpled.core import dbapi
from uncrumpled.core import responses as resp


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


def page_what_do(db, profile, book, program, hotkey):
    '''
    what to do if a page doesn't exist
    Right now, very important part of uncrumpled.

    first check if the book is set to load a loose page
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
    book_mash = json.loads(halt.load_column(db, 'Books', ('MashConfig',), cond)[0][0])
    no_process = book_mash['no_process']

    specific = None
    loose = None

    if no_process == 'read':
        raise NotImplementedError
    elif no_process == 'shelve':
        return False
    elif no_process == 'loose':
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
    elif no_process == 'write':
        pass

    elif no_process == 'bookmark':
        raise NotImplementedError
        title = util.parse_title()
        specific = title
    rowid = dbapi.page_create(db, profile, book, program, specific, loose)
    return rowid


def hotkey_pressed(core, profile, program, hotkey):
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
    if not book:
        raise Exception('This is just for testing, in production should never get here')


    page = page_find(core.db, profile, book, program)
    if not page:
        page = page_what_do(core.db, profile, book, program, hotkey)
        if page:
            yield resp.resp('page_load', page=page)
            # yield hotkey_presssed()
        else:
            yield False
    else:
        yield resp.resp('page_load', page=page)
