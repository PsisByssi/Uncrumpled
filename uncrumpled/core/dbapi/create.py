import os
import sqlite3
import logging

import halt

from uncrumpled.core.dbapi import profile_set_active

from uncrumpled.core.dbapi import profile_get_active


def new_db(database):
    '''removes old and creates new db at location and name'''
    logging.info('sqlite3 version : %s' % sqlite3.sqlite_version)
    logging.info('about to del and create the db file: %s' % database)
    try:
        os.remove(database)
    except FileNotFoundError:
        pass

    with sqlite3.connect(database) as con:
        cur = con.cursor()
        cur.execute('pragma foreign_keys = off')

        cur.execute("""CREATE TABLE UserInfo(Name TEXT,
                                           Password TEXT)""")

        cur.execute("""CREATE TABLE DefaultOptions(Name TEXT,
                                                 MashConfig TEXT)
                                                 """)

        cur.execute("""CREATE TABLE Hotkeys(Profile TEXT,
                                          Book TEXT NOT NULL,
                                          Hotkey TEXT NOT NULL,
                                          MashConfig TEXT)""")
        cur.execute(
            "CREATE UNIQUE INDEX hotkey_name ON Hotkeys(Profile, Hotkey)")

        cur.execute("""CREATE TABLE Profiles(Name TEXT PRIMARY KEY,
                                             Active INTEGER,
                                             MashConfig TEXT)""")

        cur.execute("""CREATE TABLE Books(Book TEXT NOT NULL,
                                        Profile TEXT NOT NULL,
                                        MashConfig Text)""")
        cur.execute(
            "CREATE UNIQUE INDEX book_name ON Books(Profile, Book)")

        cur.execute("""CREATE TABLE Pages(Id INTEGER PRIMARY KEY,
                                          Profile TEXT NOT NULL,
                                          Book TEXT NOT NULl,
                                          Program TEXT NOT NULL,
                                          Specific TEXT NOT NULL,
                                          Loose TEXT NOT NULL,
                                          UFile TEXT,
                                          MashConfig TEXT)""")
        cur.execute(
            "CREATE UNIQUE INDEX page_name ON Pages(Profile, Book, Program, Specific, Loose)")

        # Backlink from the file onto the page
        cur.execute("""CREATE TABLE Ufiles(UFile Text NOT NULL,
                                           Pages TEXT)""")

        cur.execute("INSERT INTO Profiles ('Name') VALUES ('default')")
        cur.execute("INSERT INTO DefaultOptions ('Name') VALUES ('user')")
        con.commit()
        defaultOptions = {'Name': 'System Default'}
        defaultOptions['no_process'] = 'new'
        defaultOptions['empty_book'] = 'homepage'
        defaultOptions['homepage'] = 1
        defaultOptions['prompt_external_link'] = 0
        defaultOptions['external_link'] = 0
        defaultOptions['win_location'] = 'center'
        defaultOptions['win_brain'] = 'session'
        defaultOptions['win_open_method'] = 'slide'
        defaultOptions['opacity'] = 0.85
        defaultOptions['opacity_brain'] = 'session'
        defaultOptions['startup_lock'] = 1
        defaultOptions['lock_memory'] = 0
        defaultOptions['edit_through_lock'] = 1
        defaultOptions['send_hotkey'] = 1
        defaultOptions['cursor_brain'] = 'session'

        halt.insert(database, 'DefaultOptions', defaultOptions, mash=True)

        print('Setting active profile after create')
        profile_set_active(database, 'default')
        print('gotten ' + profile_get_active(db=database))

    print('Database created successfully!')
