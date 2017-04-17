
#~ Restrictive license being used whereby the following apply.
#~ 1. Non-commercial use only
#~ 2. Cannot modify source-code for any purpose (cannot create derivative works)
#~ The full license can be viewed at the link below
#~ http://www.binpress.com/license/view/l/9dfa4dbfe85c336d16d1dd71a2e2cfb2
'''
an api for common tasks on the uncrumpled database
'''
import os
from contextlib import suppress
import sqlite3

import dbtools
from timstools import safe_string

from util import rand_str, symlink, readlink


def make_bookname(name, widgettype=None, profile=None, db=None):
    if not widgettype:
        assert profile
        cond = "where Book == '{0}' and Profile =='{1}'".format(
                                                   name, profile)
        cur = dbtools.loadItColumn('WidgetType','Books',cond,
                                   db=db)
        widgettype = cur.fetchone()[0]
        cur.close()
    bookname = widgettype + ' - ' + name
    return bookname

def split_bookname(bookname):
    return bookname.split(' - ')[-1]

class CreateWorkBookError(Exception): pass
class NoHotkeyError(CreateWorkBookError): pass
class UniqueNameError(CreateWorkBookError): pass
class UniqueHotkeyError(CreateWorkBookError): pass
class CreateProfileError(Exception):pass
class UniqueProfileError(CreateProfileError):pass

def create_page(book, program, profile, specific=None, db=None):
    options = {
        'PathToLoad': None,
        'Profile': profile,
        'Bookname': book,
        'Program': program,
        'Symlink': None,
        'SpecificName': specific,
        'db': db,
    }
    display_name = book.split()[0]
    condition = "where Name == '" + display_name + "'"
    cur = dbtools.loadItColumn(
                        'ClassName',
                        'WidgetTypes',
                        condition,
                        db=db)
    category = cur.fetchone()[0]

    import newPage
    new_page = eval('newPage.' + category + '(options)')
    new_page.save_instance()


def create_book(name, profile, widgettype,
                hotkey=None, db=None, **kwargs):
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

    bookname = make_bookname(name, widgettype, db=db)

# cond="where Name = '"+self.Name+"' and Profile = '"+self.Profile+"'"
    cond = "where Name = 'System Default'"
# adding Default setting on page creation, havenet finished the gui
# workbook creation, people iwll be able to choose what is added not
# automatically defaulting to system defaultTBD
    options = dbtools.loadItMash('DefaultOptions',
                                 cond,
                                 column=None,
                                 returnObj=dict,
                                 db=db)
    options.update({'Name': bookname,
                    'WidgetType': widgettype,
                    'Book': split_bookname(bookname),
                    'Profile': profile,
                    })

    for k, v in kwargs.items():
        if k not in options:
            raise KeyError(k + 'not recognized, add a default first to dbcreate.py')
        else:
            options[k] = v

    try:
        # i am doing 2 seperate queries that depend on each other
        # the cur is only commited at the end so i dont have to undo anythin on
        # a fail
        con = dbtools.storeIt(options, 'Books', mashconfig=True,
                              commit=False, db=db)
        if hotkey:
            assert type(hotkey) != str
            _add_hotkey(hotkey, profile, bookname, con)
            con.commit()
        else:
            raise NoHotkeyError
    except sqlite3.IntegrityError as err:
        raise UniqueNameError('Name for that widget already exists!')
    finally:
        with suppress(UnboundLocalError):
            print('closing db')
            con.close()


def _add_hotkey(full_hotkey, profile, bookname, con=None):
    '''
    creates a new hotkey entry

    This doesn't commit to the database,
    createnewworkbook handles the commits so if there is an error later on
    no hotkey field will be added.
    just as a side note incase this gets called directly later
    '''
    hk_options = {'Hotkey': full_hotkey, 'Profile': profile, 'Bookname': bookname}
    try:
        dbtools.storeIt(hk_options, 'Hotkeys', con=con)
    except sqlite3.IntegrityError as err:
        raise UniqueHotkeyError(str(err))


def create_profile(name, db=None):
    '''
    saves a new profile entry in the database
    '''
    # Todo No subclassed profiles as of yet.
    try:
        dbtools.storeIt({"name": name}, 'Profiles', db=db)
    except Exception:
        raise UniqueProfileError


def create_link(app, uncpath, filepath, db=None):
    '''
    point a uncpath to a specifc file
    this is done by reading the symlink and modifying it

    TODO if the uncpath doesn't exist it will be created
    '''
    # profile, book, program, specific = parse_address(
                                                # filepath, db=db)
    get_my_link = name_from_address(filepath)
    update_my_link = name_from_address(uncpath)
    cur = dbtools.loadItColumn('Symlink', table='Pages',
            condition="where Name == '{}'".format(get_my_link))

    # new_link_path = readlink(os.path.join(app.symlinkdir,
                                            # cur.fetchone()[0]))

    name = cur.fetchone()[0]
    new_link_path = readlink(os.path.join(app.symlinkdir,
                                            name))
    cur = dbtools.loadItColumn('Symlink', table='Pages',
            condition="where Name == '{}'".format(update_my_link))
    old_link_name = cur.fetchone()[0]

    update_me = os.path.join(app.symlinkdir, old_link_name)
    print('from ', get_my_link)
    print('from ', filepath)
    print('updating {} from {} -> {}'.format(old_link_name, name, new_link_path))
    print('the symlink from the other file ', readlink(os.path.join(app.symlinkdir, old_link_name)))
    os.remove(update_me)
    symlink(new_link_path, update_me)


def make_filepath(app, page, overwrite=False):
    '''
    :return: symlink name (used just like normal file)
    side effect -> creates the symlink, and optionally the file
    will raise FileExistsError if overwrite is False
    '''
    # the file on disk is given a random name.
    # This is pointed to by a symlink named as the page address
    # This is so that pages can have address that point to
    # any file.
    symlink_name = (safe_string(page.Bookname) \
              + safe_string(page.Program) \
              + safe_string(page.HotkeyHumanReadable) \
              + safe_string(page.Profile)).replace(' ', '_')

    dest = os.path.join(app.symlinkdir, symlink_name)
    fname = _rand_name_in_dir(app.notedir) + '.txt'
    src = os.path.join(app.notedir, fname)
    symlink(src, dest)
    app.uac_bypass(src, create=True, overwrite=overwrite)
    return symlink_name


def _rand_name_in_dir(dir):
    '''returns a str not found in a dir'''
    fname = rand_str(8)
    while fname in os.listdir(dir):
        fname = rand_str(8)
    return fname


def all_profiles(db=None):
    '''
    Returns a list of profiles on the system
    '''
    cur = dbtools.loadItColumn('Name', 'Profiles', db=db)
    return [x[0] for x in cur.fetchall()]


def delete_profile(profile, db=None):
    condition = "where Name == '{0}'".format(profile)
    dbtools.deleteIt('Profiles', condition, db=db)


def set_active_profile(profile, db=None):
    '''Sets the given profile as being active'''
    # Remove the previous active
    cond = "where Active == 1"
    dbtools.updateIt(False,
                    column='Active',
                    table='Profiles',
                    mashconfig=False,
                    condition=cond,
                    db=db)

    # Update the new
    cond = "where Name == '{0}'".format(profile)
    dbtools.updateIt(True,
                     column='Active',
                     table='Profiles',
                     mashconfig=False,
                     condition=cond,
                     db=db)


def get_active_profile(db=None):
    '''Returns the currently active profile'''
    cond = "where Active == 1"
    cur = dbtools.loadItColumn(column='Name',
                               table='Profiles',
                               condition=cond,
                               db=db)
    profile = cur.fetchone()[0]
    return profile


def get_hotkeys(profile, db=None):
    '''returns a list of all hotkeys for a given profile'''
    hotkeys = []
    condition = "where Profile is '" + profile + "'"
    cur = dbtools.loadItColumn('Hotkey', 'Hotkeys', condition, db=db)
    for hotkey in cur.fetchall():
        hotkeys.append(dbtools.turnIntoObj(hotkey))
    return hotkeys


def delete_workbook(name, widgettype=False, profile=None, db=None):  # tbd PROFILE
    '''
    either user entered name and widget type/archetype or
    pass in the book name as name
    Tbd give the option to ssave old pages or move to another
    workbook or sth...?
    '''
    assert profile
    if widgettype:
        bookname = make_bookname(name, widgettype, db=db)
    else:
        bookname = name
    # Close any open windows
    # for note in note_references.values():
    # if note.page.Bookname == bookname:
    # note.toplevel.destroy()

    condition = "where Name == '{0}' and Profile == '{1}'"\
                    .format(bookname, profile)
    dbtools.deleteIt('Books', condition, db=db)

    condition = "where Bookname == '{0}' and Profile =='{1}'"\
                    .format(bookname, profile)
    # TBD throws no error if name doesn't exist
    dbtools.deleteIt('Hotkeys', condition, db=db)
    dbtools.deleteIt('Pages', condition, db=db)

# Remember to Update values that other colums depend on first


def up_b_hotkey(value, bookname, db=None):
    '''
    Update The hotkey for a Book
    returns the old keycode so you can unregister the key if you wish
    '''
    condition = "where Bookname =='" + bookname + "'"
    old_hk = dbtools.turnIntoObj(dbtools.loadItColumn('Hotkey', 'Hotkeys',
                                                      condition).fetchone()[0])
    try:
        dbtools.updateIt({'Hotkey': value},
                         True,
                         'Hotkeys',
                         condition,
                         db=db)
    except:
        raise UniqueHotkeyError('Hotkey not unique')
    return old_hk


def up_b_bookname(user_entered_name, oldname, db=None):
    '''
    Update name of a book
    Make sure to overwirte the old bookname,
    Make sure to pass in only the user entered part of the name
    '''
    widgettype = oldname.split('-')[0].strip()
    newname = ' - '.join((widgettype, user_entered_name))

    dbtools.updateIt(newname,
                     'Name',
                     'Books',
                     "where Name =='" + oldname + "'",
                     mashconfig=False,
                     db=db)
    condition = "where Bookname =='" + oldname + "'"
    for data in dbtools.loadItColumn('Name, Program, Profile',
                                    'Pages',
                                     condition).fetchall():
        page, program, profile = data
        rest = page[len(oldname):]
        dbtools.updateIt(
            newname + rest,
            'Name',
            'Pages',
            condition + " and Program == '{0}' and Profile == '{1}'".format(
                program, profile),
            mashconfig=False)
    dbtools.updateIt(newname, 'Bookname', 'Pages', condition, mashconfig=False)
    dbtools.updateIt(newname,
                     'Bookname',
                     'Hotkeys',
                     condition,
                     mashconfig=False)
    return newname

def up_b_mash(book, key, value, db=None):
    dbtools.updateIt({key:value},
                     None,
                     'Books',
                     "where Name =='" + book + "'",
                     mashconfig=True,
                     db=db)

def delete_page(profile, bookname, program, specific, db=None):
    '''Delete a page from a workbook'''
    pagename = name_from_kwrds(
                        profile, bookname, program, specific)

    #~ for note in note_references.values():
    #~ if note.page.Name == pagename:
    #~ note.toplevel.destroy()

    condition = "where Name == '{0}'".format(pagename)
    dbtools.deleteIt('Pages', condition, db=db)


def all_books(widgettype=True, db=None):
    '''
    return all workbook names
    '''
    cur = dbtools.loadItColumn('Name', 'Books', db=db)
    if widgettype:
        return [x[0] for x in cur.fetchall()]
    else:
        return [split_bookname(x[0]) for x in cur.fetchall()]


def make_page_address(Profile, Bookname, Program,
                      SpecificName=None):
    '''
    a more readable format for a page
    '''
    book = split_bookname(Bookname)
    if not SpecificName:
        args = (Profile, book, Program)
    else:
        args = (Profile, book, Program, SpecificName)
    return '/'.join(args)


def parse_address(address, db=None):
    split = address.split('/')
    if len(split) == 3:
        profile, book, program = split
        specific = None
    else:
        print('split ', split)
        profile, book, program, specific = split
    bookname = make_bookname(book, profile=profile, db=db)
    return profile, bookname, program, specific


def get_loose_page(book, db_cursor):
    cond = "SELECT Bookname,Profile,PathToLoad,\
                Symlink,SpecificName,MashConfig from Pages \
                where Bookname == '" + book + "'\
                AND Program == ''"
    db_cursor.execute(cond)
    Bookname, Profile, PathToLoad,\
            Symlink, SpecificName,\
            MashConfig = db_cursor.fetchone()
    db_cursor.close()
    return None, Bookname, None, Profile,\
            Symlink, MashConfig, SpecificName


def name_from_address(address,db=None):
    return name_from_kwrds(*parse_address(address, db=db))


def name_from_kwrds(profile, bookname, program, specific):
    '''
    bookname includes the archetype info,
    use make_bookname
    '''
    if specific == None:
        specific = ''
    if program == None:
        program = ''
    return bookname + program + profile + specific


def get_page_col(col, address, db=None):
    name = name_from_address(address)
    condition = "where Name == '" + name + "'"
    cur =  dbtools.loadItColumn(col, 'Pages', condition, db=db)
    result = cur.fetchone()[0]
    cur.close()
    return result

if __name__ == '__main__':
    print(list(all_pages()))
