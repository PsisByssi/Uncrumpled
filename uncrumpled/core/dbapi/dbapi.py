'''
    talks to sql db using halt
'''
import sqlite3
from contextlib import suppress
import json

import halt

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
            con.commit()
        else:
            raise NoHotkeyError
    except halt.HaltException:
        raise UniqueNameError('Name for that widget already exists!')
    finally:
        with suppress(UnboundLocalError):
            con.close()


def _add_hotkey(db, hotkey, profile, book, con=None):
    assert type(hotkey) in (tuple, dict, list)
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

    # cond = "where Book == '{0}' and Profile =='{1}'"\
                    # .format(bookname, profile)
    halt.delete(db, 'Hotkeys', cond)
    halt.delete(db, 'Pages', cond)
    # Remember to Update values that other colums depend on first
    return True


def book_get_all(db):
    results = halt.load_column(db, 'Books', ('Book',))
    return [x[0] for x in results]


def hotkey_get_all(db, profile):
    '''returns a list of all hotkeys for a given profile'''
    hotkeys = []
    cond = "where Profile == '" + profile + "'"
    for hk in  halt.load_column(db, 'Hotkeys', ('Hotkey',), cond):
        hotkeys.append(halt.objectify(hk))
    return hotkeys


def _page_save(profile, book, program, specific):
    assert type(program) in (list, tuple)
    to_save = {
        'Profile': profile,
        'Book': book,
        'Program': program,
        'Symlink': None,
        'SpecificName': specific,
    }

    if specific is None:
        specific = ''
    if program is None:
        program = ''

    name = book + program[0] + profile + specific # TODO improve this
    cond = "where Name == '{0}'".format(name)
    return to_save, cond


def page_create(db, profile, book, program, specific):
    to_save, cond = _page_save(profile, book, program, specific)
    halt.insert(db, 'Pages', to_save, mash=False, commit=True)


def page_update(db, profile, book, program, specific):
    to_save, cond = _page_save(profile, book, program, specific)
    halt.update(db, 'Pages', to_save, mash=False, commit=True)


def page_get_all(db, address=True):
    '''
    return eith as address
    or profile book, program, program, specific
    '''
    columns = ('Book', 'Program', 'Profile', 'SpecificName')
    results = halt.load_column(db, 'Pages', columns)
    if address:
        for row in results:
            Book, Program, Profile, SpecificName = row
            yield make_page_address(
                    Profile, Book, Program, SpecificName)
    else:
        for row in results:
            Book, Program, Profile, SpecificName = row
            yield Profile, Book, Program, SpecificName


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


