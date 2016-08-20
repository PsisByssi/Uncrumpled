'''
    talks to sql db using halt
'''

import sqlite3
from contextlib import suppress
import json

import halt

from uncrumpled.core.dbapi import util

class CreateWorkBookError(Exception): pass
class NoHotkeyError(CreateWorkBookError): pass
class UniqueNameError(CreateWorkBookError): pass
class UniqueHotkeyError(CreateWorkBookError): pass


def book_create(db, profile, book, hotkey, **kwargs):
    '''
    For creating a new workbook, NOT updating one

    use this with the exceptions
    NoHotkeyError
    UniqueNameError
    UniqueHotkeyError

    On no hotkey the book will still be created

    No changes to db on the other errors

    on success returns the  keycode and masks
    '''
    cond = "where Name = 'System Default'"
    options = halt.load_column(db, 'DefaultOptions', ('MashConfig',), cond)
    options = halt.objectify(options[0][0])
    for k, v in kwargs.items():
        if k not in options:
            raise KeyError(k + 'not recognized, add a default first to dbapi.py')
        else:
            options[k] = v

    options['Book'] = book
    options['Profile'] = profile

    try:
        # i am doing 2 seperate queries that depend on each other
        # the cur is only commited at the end so i dont have to undo anythin on
        # a fail
        if hotkey:
            con = halt.insert(db, 'Books', options, mash=True, commit=False)
            _add_hotkey(db, hotkey, profile, book, con)
            con.commit() # TODO delete
        else:
            raise NoHotkeyError
    except halt.HaltException:
        raise UniqueNameError('Name for that widget already exists!')
    finally:
        with suppress(UnboundLocalError):
            con.close()


def _add_hotkey(db, hotkey, profile, book, con=None):
    assert type(hotkey) == list
    hotkey = json.dumps(hotkey)
    options = {'Hotkey': hotkey, 'Profile': profile, 'Book': book}
    try:
        halt.insert(db, 'Hotkeys', options, con=con)
    except halt.HaltException as err:
        raise UniqueHotkeyError(str(err))


def book_delete(db, book, profile):
    if book not in book_get_all(db):
        return False
    cond = "where Book == '{0}' and Profile == '{1}'"\
                    .format(book, profile)
    halt.delete(db, 'Books', cond)
    halt.delete(db, 'Hotkeys', cond)
    halt.delete(db, 'Pages', cond)
    # Remember to Update values that other colums depend on first
    return True


def book_get_all(db):
    results = halt.load_column(db, 'Books', ('Book',))
    return [x[0] for x in results]


def hotkey_create(db, profile, book, hotkey):
    try:
        con = sqlite3.connect(db)
        _add_hotkey(db, hotkey, profile, book)
        con.commit()
    except UniqueHotkeyError:
        return False
    else:
        return True
    finally:
        with suppress(UnboundLocalError):
            con.close()


def hotkey_delete(db, profile, book, hotkey):
    assert type(hotkey) == list
    if hotkey in hotkey_get_all(db, profile):
        cond = "WHERE Profile=='{}' AND Book=='{}'".format(profile, book)
        halt.delete(db, 'Hotkeys', cond)
        return True
    return False


def hotkey_update(db, profile, book, hotkey):
    assert type(hotkey) == list
    if hotkey in hotkey_get_all(db, profile):
        to_update={'Profile': profile, 'Book': book, 'Hotkey': hotkey}
        cond = "WHERE Profile=='{}' AND Book=='{}'".format(profile, book)
        halt.update(db, 'Hotkeys', to_update, cond=cond)
        return True
    return False


def hotkey_get_all(db, profile):
    '''returns a list of all hotkeys for a given profile'''
    hotkeys = []
    cond = "where Profile == '" + profile + "'"
    for hk in  halt.load_column(db, 'Hotkeys', ('Hotkey',), cond):
        hotkeys.append(halt.objectify(hk[0]))
    return hotkeys


def _page_save(profile, book, program, specific, loose):
    if not program: program = util.UNIQUE_NULL
    if not specific: specific = util.UNIQUE_NULL
    if not loose: loose = util.UNIQUE_NULL

    to_save = {
        'Profile': profile,
        'Book': book,
        'Program': program,
        'Symlink': None,
        'Specific': specific,
        'Loose': loose,
    }
    return to_save


def page_create(db, profile, book, program, specific, loose):
    to_save = _page_save(profile, book, program, specific, loose)
    try:
        halt.insert(db, 'Pages', to_save, mash=False, commit=True)
    except halt.HaltException:
        return False
    return True


def page_update(db, profile, book, program, specific, loose):
    rowid = util.page_rowid_get(db, profile, book, program, specific, loose)
    if rowid:
        to_update = _page_save(profile, book, program, specific, loose)
    # if page in page_get_all(db):
        cond = "WHERE Id == {}".format(rowid)
        halt.update(db, 'Pages', to_update, cond=cond, mash=False)
        return True
    return False


def page_delete(db, profile, book, program, specific, loose):
    rowid = util.page_rowid_get(db, profile, book, program, specific, loose)
    if rowid:
        cond = "WHERE Id == {}".format(rowid)
        halt.delete(db, 'Pages', cond)
        return True
    return False


def page_get_all(db):
    '''
    return eith as address
    or profile book, program, program, specific, loose
    '''
    columns = ('Profile', 'Book', 'Program', 'Specific', 'Loose')
    results = halt.load_column(db, 'Pages', columns)
    for row in results:
        yield row


def profile_create(db, name):
    '''
    saves a new profile entry in the database
    '''
    try:
        halt.insert(db, 'Profiles', {"name": name})
    except halt.HaltException:
        return False
    else:
        return True


def profile_delete(db, profile):
    if profile not in profile_get_all(db):
        return False
    cond = "where Name == '{0}'".format(profile)
    halt.delete(db, 'Profiles', cond)
    return True


def profile_set_active(db, profile):
    '''Sets the given profile as being active'''
    # Remove the previous active
    cond = "where Active == 1"
    halt.update(db, 'Profiles', {'Active': False}, cond)

    # Update the new
    cond = "where Name == '{0}'".format(profile)
    halt.update(db, 'Profiles', {'Active': True},  cond)


def profile_get_active(db):
    '''Returns the currently active profile'''
    cond = "where Active == 1"
    results = halt.load_column(db, 'Profiles', ('Name',), cond)
    profile = results[0][0]
    return profile


def profile_get_all(db):
    ''' Returns a list of profiles on the system '''
    results = halt.load_column(db, 'Profiles', ('Name',))
    return [x[0] for x in results]


