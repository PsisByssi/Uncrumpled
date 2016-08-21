'''
    Tests requests against the core

    We only check the messages are correct,
    There are a few asserts for database stuff but those
    should be deleted if i need to do some db tests
'''

import asyncio
import tempfile
import os
import shutil
from types import GeneratorType

import pytest
import halt
import peasoup

from uncrumpled.core import requests as req
from uncrumpled.core import dbapi, Core
from util import get_all_data


class MixIn():
    profile = 'test profile'
    book = 'test book'
    program = 'testprogram'
    hotkey = ['f5']
    specific = None
    loose = None
    def setup_class(cls):
        cls.tdir = tempfile.mkdtemp()
        # cls.db = os.path.join(cls.tdir, 'test.db')
        # dbapi.new_db(cls.db)
        cls.core = Core(db='')
        cls.event_loop = asyncio.get_event_loop()

    def teardown_class(cls):
        shutil.rmtree(cls.tdir)
        cls.event_loop.close()

    def setup_method(self, func):
        '''create fresh database for each test method'''
        self.core.db = os.path.join(self.tdir, func.__name__+'.db')
        try:
            os.remove(self.core.db)
        except FileNotFoundError:
            pass
        dbapi.new_db(self.core.db)

    def run(self, func, *args, **kwargs):
        '''
        some isolation if we change from generaotrs
        '''
        res = func(*args, **kwargs)
        if type(res) != GeneratorType:
            return res
        else:
            res = list(res)
            if len(res) == 1:
                return res[0]
            if res == []:
                return False
            return res


class TestProfile(MixIn):
    def test_profile_create(self):
        response = self.run(req.profile_create, self.core, 'new')
        assert 'profile created' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1

        response = self.run(req.profile_create, self.core, 'new')
        assert 'profile already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1


    def test_profile_delete(self):
        response = self.run(req.profile_delete, self.core, 'bad_profile')
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = self.run(req.profile_create, self.core, 'new')

        response = self.run(req.profile_delete, self.core, 'new')
        assert 'profile deleted' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1


    def test_profile_set_and_get_active(self):
        profile = 'test'
        self.run(req.profile_create, self.core, profile)
        response = self.run(req.profile_set_active, self.core, profile)
        assert 'profile changed' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Profiles')

        response = self.run(req.profile_get_active, self.core)
        abc = response
        response['output_method'] == 'noop'
        cond = "where Name == '{}'".format('default')
        default_active = halt.load_column(self.core.db, 'Profiles', ('Active',), cond)
        assert not default_active[0][0]
        cond = "where Name == '{}'".format(profile)
        test_active = halt.load_column(self.core.db, 'Profiles', ('Active',), cond)
        assert test_active[0][0]


class TestBook(MixIn):
    active_profile = 'default'

    def setup_method(self, func):
        super().setup_method(func)
        req.profile_create(self.core, self.profile)

    def test_book_create(self):
        response = self.run(req.book_create, self.core, self.profile, self.book,
                                   self.hotkey, self.active_profile)
        assert 'book created' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Books')[0]
        assert data[0] == self.book
        assert data[1] == self.profile

        response = self.run(req.book_create, self.core, self.profile, self.book,
                                   self.hotkey, self.active_profile)
        assert 'book already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        book2 = 'asdf'
        response = self.run(req.book_create, self.core, self.profile, book2,
                                   self.hotkey, self.active_profile)
        assert 'hotkey already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = self.run(req.book_create, self.core, self.profile, book2,
                                   '', self.active_profile)
        assert 'hotkey is required' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        # Hit the code path where hokteys would get reloaded, they don't as
        # old == new, it's a state based operation, not testing for it atm
        hotkey2 = ['f7']
        self.run(req.profile_create, self.core, self.profile)
        self.run(req.profile_set_active, self.core, self.profile)
        response = self.run(req.book_create, self.core, self.profile, book2,
                                   hotkey2, self.profile)



    def test_book_delete(self):
        response = self.run(req.book_delete, self.core, 'bad_book', self.profile)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = self.run(req.book_create, self.core, self.profile, self.book,
                                   self.hotkey, self.active_profile)

        response = self.run(req.book_delete, self.core, self.book, self.profile)
        assert 'book deleted' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Books')
        assert not data

        response = self.run(req.book_delete, self.core, self.book, self.profile)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1


class TestPage(MixIn):
    page = 'testpage'

    def test_page_create(self):
        response = self.run(req.page_create, self.core, self.profile, self.book,
                                   self.program, self.specific)
        assert 'page created' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Pages')[0]
        assert data[1] == self.profile
        assert data[2] == self.book
        assert data[3] == self.program

        response = self.run(req.page_create, self.core, self.profile, self.book,
                                   self.program, self.specific)
        assert 'page already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1


    def test_page_delete(self):
        response = self.run(req.page_delete, self.core, self.profile, self.book,
                                    'bad_page', self.specific, self.loose)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = self.run(req.page_create, self.core, self.profile, self.book,
                                   self.program, self.specific)


        data = get_all_data(self.core.db, 'Pages')
        response = self.run(req.page_delete, self.core, self.profile, self.book,
                                    self.program, self.specific, self.loose)
        assert 'page deleted' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Pages')
        assert not data

        response = self.run(req.page_delete, self.core, self.profile, self.book,
                                    self.program, self.specific, self.loose)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

    def test_page_update(self):
        response = self.run(req.page_update, self.core, self.profile, self.book,
                                    'bad_page', self.specific, self.loose)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = self.run(req.page_create, self.core, self.profile, self.book,
                                   self.program, self.specific)
        data = get_all_data(self.core.db, 'Pages')

        response = self.run(req.page_update, self.core, self.profile, self.book,
                                   self.program, self.specific)
        assert 'page saved' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(self.core.db, 'Pages')[0]
        assert data[1] == self.profile
        assert data[2] == self.book
        assert data[3] == self.program


class TestHotkeys(MixIn):

    def test_hotkey_create(self):
        response = self.run(req.hotkey_create, self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'created' in response['key']

        response = self.run(req.hotkey_create, self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'taken' in response['key']


    def test_hotkey_delete(self):
        response = self.run(req.hotkey_delete, self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'not_found' in response['key']

        response = self.run(req.hotkey_create, self.core, self.profile, self.book,
                                     self.hotkey)

        response = self.run(req.hotkey_delete, self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'deleted' in response['key']


    def test_hotkey_updated(self):
        response = self.run(req.hotkey_update, self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'not_found' in response['key']

        response = self.run(req.hotkey_create, self.core, self.profile, self.book,
                                     self.hotkey)

        response = self.run(req.hotkey_update, self.core, self.profile, self.book,
                                     self.hotkey)
        assert 'updated' in response['key']
        hotkey2 = ['f11']
        response = self.run(req.hotkey_update, self.core, self.profile, self.book,
                                     hotkey2)
        assert 'not_found' in response['key']


    def test_hotkey_load(self):
        response = self.run(req.hotkeys_load, self.core, self.profile)
        assert not response
        dbapi.profile_create(self.core.db, self.profile)
        response = self.run(req.hotkeys_load, self.core, self.profile)
        assert not response

        dbapi.hotkey_create(self.core.db, self.profile, self.book, self.hotkey)
        hotkey2 = ['f11']
        dbapi.hotkey_create(self.core.db, self.profile, self.book, hotkey2)
        response = self.run(req.hotkeys_load, self.core, self.profile)

        assert response[0]['output_method'] == 'system_hotkey_register'
        assert response[0]['output_kwargs']['hotkey'] in (self.hotkey, hotkey2)
        assert response[1]['output_method'] == 'system_hotkey_register'
        assert response[1]['output_kwargs']['hotkey'] in (self.hotkey, hotkey2)


    def test_hotkeys_reload(self):
        response = self.run(req.hotkeys_reload, self.core, 'default', self.profile)
        assert not response

        dbapi.profile_create(self.core.db, self.profile)
        dbapi.hotkey_create(self.core.db, 'default', self.book, self.hotkey)
        dbapi.hotkey_create(self.core.db, self.profile, self.book, self.hotkey)
        response = self.run(req.hotkeys_reload, self.core, 'default', self.profile)
        assert response[0]['output_method'] == 'system_hotkey_unregister'
        assert response[1]['output_method'] == 'system_hotkey_register'


class TestUiInit(MixIn):
    def test_first_run(self):
        self.first_run = True
        response = self.run(req.ui_init, self.core, self.first_run)
        assert 'show_window' == response[0]['output_method']
        assert 'welcome_screen' == response[1]['output_method']
        assert 'book_create' == response[2]['input_method']
        assert 'page_create' == response[3]['input_method']
        assert 'book_create' == response[4]['input_method']
        assert 'profile_set_active' == response[5]['output_method']
        assert len(response) == 8

    def test_first_run_with_profile_active(self):
        self.first_run = True
        dbapi.profile_create(self.core.db, self.profile)
        dbapi.hotkey_create(self.core.db, 'default', self.book, self.hotkey)
        dbapi.hotkey_create(self.core.db, self.profile, self.book, self.hotkey)
        response = self.run(req.ui_init, self.core, self.first_run)
        assert response[6]['output_method'] == 'system_hotkey_register'
        assert len(response) == 9

    def test_all_other_runs(self):
        self.first_run = False
        response = self.run(req.ui_init, self.core, self.first_run)
        assert 'profile_set_active' == response['output_method']

    def test_all_other_runs_with_profile_active(self):
        self.first_run = False
        dbapi.profile_create(self.core.db, self.profile)
        dbapi.hotkey_create(self.core.db, 'default', self.book, self.hotkey)
        dbapi.hotkey_create(self.core.db, self.profile, self.book, self.hotkey)
        response = self.run(req.ui_init, self.core, self.first_run)
        assert response[1]['output_method'] == 'system_hotkey_register'
        assert len(response) == 2


#TODO move to own file
class TestPageFind(MixIn):
    specific = 'banking.com/page'
    program = 'testprogram'
    '''
    def test_can_find_a_specific_page(self):
        dbapi.profile_create(self.core.db, self.profile)
        dbapi.page_create(self.core.db, self.profile, self.book, self.program, None, None)
        dbapi.page_create(self.core.db, self.profile, self.book, self.program, self.specific, None)
        # resp = self.run(req.page_find, self.core.db, self.profile, self.book, self.program)
        data = get_all_data(self.core.db, 'Pages')[0]
        assert resp[4] == self.specific

    '''
    def test_page_find_general(self):
        dbapi.profile_create(self.core.db, self.profile)
        assert dbapi.page_create(self.core.db, self.profile, self.book, self.program, None, None)
        assert dbapi.page_create(self.core.db, self.profile, self.profile, self.program, 'some specifc', None)
        resp = self.run(req.page_find, self.core.db, self.profile, self.book, self.program)
        assert resp
        rowid = resp
        data = get_all_data(self.core.db, 'Pages')[0]
        assert data[1] == self.profile
        assert data[2] == self.book
        assert data[3] == self.program
        assert data[4] == dbapi.UNIQUE_NULL


class TestNoProcess(MixIn):
    def test_basic(s):
        kwargs = {'no_process': 'shelve'}
        dbapi.book_create(s.core.db, s.profile, s.book, s.hotkey, **kwargs)
        resp = s.run(req.no_process, s.core, s.profile, s.book, s.program, s.hotkey)
        assert resp is False

    def test_general(s):
        kwargs = {'no_process': 'write'}
        dbapi.book_create(s.core.db, s.profile, s.book, s.hotkey, **kwargs)
        resp = s.run(req.no_process, s.core, s.profile, s.book, s.program, s.hotkey)
        assert resp

        # kwargs = {'no_process': 'loose'}
        # dbapi.book_create(s.core.db, s.profile, s.book, s.hotkey, **kwargs)
        # resp = s.run(req.no_process, s.core, s.profile, s.book, s.program, s.hotkey)


    # Not sure how/what i want to do, also what about a settings file???? argh
    def test_settings_inheritance(self):
        pass

    def test_settings_composition(self):
        pass


class TestHotkeyPressed(MixIn):
    def test_general_page(s):
        # Test a note gets created if need be
        dbapi.profile_create(s.core.db, s.profile)
        kwargs = {'no_process': 'write'}
        dbapi.book_create(s.core.db, s.profile, s.book, s.hotkey, **kwargs)
        program, pid, = peasoup.process_exists()
        system = {}

        resp = s.run(req.hotkey_pressed, s.core, s.profile, program, s.hotkey,
                     system)
        assert resp[0]['input_method'] == 'page_create'

        assert resp[1]['output_method'] == 'page_load'
        system = {1: {'is_open': False}}
        assert resp[1]['output_kwargs']['page_id'] == 1

        # Now test we can load it on the next key press
        resp = s.run(req.hotkey_pressed, s.core, s.profile, program, s.hotkey,
                     system)
        resp['output_method'] == 'page_load'
        assert resp['output_kwargs']['page_id'] == 1


        # Test the close signal gets sent if it is already open
        resp = s.run(req.hotkey_pressed, s.core, s.profile, program, s.hotkey,
                     system)
        resp['output_method'] == 'page_close'
        assert resp['output_kwargs']['page_id'] == 1

