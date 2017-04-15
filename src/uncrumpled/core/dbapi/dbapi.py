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


# TODO SWITCH book, profile to profile, book
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


def book_update(db, book, profile, to_update):
    '''
    Required a dict that will update columns or mash
    return False if book doesn't exist
    return True if update succesful
    '''
    if not book_get(db, profile, book):
        return False
    cond = "where Book == '{0}' and Profile == '{1}'".format(book, profile)
    halt.update(db, 'Books', to_update, cond, mash=True)
    return True


def book_get(db, profile, book):
    '''get all info for a book'''
    cond = "where Book == '{0}' and Profile == '{1}'".format(book, profile)
    res = halt.load_row(db, 'Books', cond)
    if not res:
        return False
    return res[0]


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


def hotkey_get(db, profile, book) -> list:
    ''' get single hotkey based on profile and book'''
    cond = "WHERE Profile=='{}' AND Book=='{}'" .format(profile, book)
    hk = halt.load_column(db, 'Hotkeys', ('Hotkey',), cond)
    try:
        hk = halt.objectify((hk[0][0]))
    except Exception:
        return []
    return hk


def loose_get_all(db, profile):
    '''returns a list of all loose pages for a given profile'''
    filenames = []
    cond = "where Profile == '" + profile + "'"
    for fname in  halt.load_column(db, 'Pages', ('Loose',), cond):
        fname = fname[0]
        if fname not in util.UNIQUE_NULL:
            filenames.append(fname)
    return filenames


def _page_save(profile, book, program, specific, loose):
    if not program: program = util.UNIQUE_NULL
    if not specific: specific = util.UNIQUE_NULL
    if not loose: loose = util.UNIQUE_NULL

    to_save = {
        'Profile': profile,
        'Book': book,
        'Program': program,
        'UFile': None,
        'Specific': specific,
        'Loose': loose,
    }
    return to_save


def page_create(db, profile, book, program, specific, loose):
    to_save = _page_save(profile, book, program, specific, loose)
    try:
        id = halt.insert(db, 'Pages', to_save, mash=False, commit=True)
        return id
    except halt.HaltException:
        return False


# TODO LOGIC COMPLETLEY BROKEN.. JUST DEL...
def page_update(db, profile, book, program, specific, loose):
    rowid = page_rowid_get(db, profile, book, program, specific, loose)
    if rowid:
        to_update = _page_save(profile, book, program, specific, loose)
        cond = "WHERE Id == {}".format(rowid)
        halt.update(db, 'Pages', to_update, cond=cond, mash=False)
        return True
    return False


def _update(data):
    if data.get('Program') == None: data['Program'] = util.UNIQUE_NULL
    if data.get('Specific') == None: data['Specific'] = util.UNIQUE_NULL
    if data.get('Loose') == None: data['Loose'] = util.UNIQUE_NULL
    return data


def page_update_from_id(db, rowid, data):
    '''
    Required a dict that will update columns or mash
    return False if page doesn't exist
    return True if update succesful
    '''
    if not page_get(db, rowid):
        return False
    update = _update(dict(data))
    cond = "WHERE Id == {}".format(rowid)
    halt.update(db, 'Pages', update, cond=cond, mash=True)
    return True


def page_delete(db, profile, book, program, specific, loose):
    rowid = page_rowid_get(db, profile, book, program, specific, loose)
    if rowid:
        cond = "WHERE Id == {}".format(rowid)
        halt.delete(db, 'Pages', cond)
        return True
    return False


def page_get(db, rowid):
    '''get all info  for a page'''
    res = halt.load_row(db, 'Pages', "WHERE Id == {}".format(rowid))
    if not res:
        return False
    return res[0]


def page_get_all(db):
    '''
    return eith as address
    or profile book, program, program, specific, loose
    '''
    columns = ('Profile', 'Book', 'Program', 'Specific', 'Loose')
    results = halt.load_column(db, 'Pages', columns)
    for row in results:
        yield row


def page_rowid_get(db, profile, book, program, specific, loose):
    page = util.page_validate(profile, book, program, specific, loose)
    cond = "WHERE Profile == '{}' AND \
                  Book == '{}' AND \
                  Program == '{}' AND \
                  Specific == '{}' AND \
                  Loose == '{}'".format(*page)
    rowid = halt.load_column(db, 'Pages', ('Id',), cond=cond)
    if not rowid:
        return False
    else:
        return rowid[0][0]


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


def profile_get(db, profile):
    '''Returns all info of a profile'''
    res = halt.load_row(db, 'Profiles', "WHERE Name == '{}'".format(profile))
    if not res:
        return False
    return res[0]


def profile_get_all(db):
    ''' Returns a list of profiles on the system '''
    results = halt.load_column(db, 'Profiles', ('Name',))
    return [x[0] for x in results]


def profile_update(db, profile, data):
    '''
    Required a dict that will update columns or mash
    return False if profile doesn't exist
    return True if update succesful
    '''
    if not profile_get(db, profile):
        return False
    cond = "WHERE Name == '{}'".format(profile)
    halt.update(db, 'Profiles', data, cond=cond, mash=True)
    return True


def ufile_create(db, page_id, file):
    cond = "WHERE Id == '{}'".format(page_id)
    obj = {'UFile': file}
    halt.update(db, 'Pages', obj, cond)

    obj['Pages'] = json.dumps([page_id])
    halt.insert(db, 'UFiles', obj, mash=False)
