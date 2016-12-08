'''
    Tests requests against the core
'''

import pytest
import halt
import peasoup
import os
import shutil

from uncrumpled.core import requests as req
from uncrumpled.core import dbapi
from uncrumpled.core.requests.config import KEYMAP_FILES
from util import get_all_data, UNCRUMPLED, MixInTestHelper
from util import EasyUncrumpled


class TestProfile(MixInTestHelper):
    def test_profile_create(s):
        response = s.run(req.profile_create, s.app, 'new')
        assert 'profile created' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1

        response = s.run(req.profile_create, s.app, 'new')
        assert 'profile already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1


    def test_profile_delete(s):
        response = s.run(req.profile_delete, s.app, 'bad_profile')
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = s.run(req.profile_create, s.app, 'new')

        response = s.run(req.profile_delete, s.app, 'new')
        assert 'profile deleted' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1


    def test_profile_set_and_get_active(s):
        profile = 'test'
        s.run(req.profile_create, s.app, profile)
        response = s.run(req.profile_set_active, s.app, profile)
        assert 'profile changed' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(s.app.db, 'Profiles')

        response = s.run(req.profile_get_active, s.app)
        abc = response
        response['output_method'] == 'noop'
        cond = "where Name == '{}'".format('default')
        default_active = halt.load_column(s.app.db, 'Profiles', ('Active',), cond)
        assert not default_active[0][0]
        cond = "where Name == '{}'".format(profile)
        test_active = halt.load_column(s.app.db, 'Profiles', ('Active',), cond)
        assert test_active[0][0]


class TestBook(MixInTestHelper):
    active_profile = 'default'

    def setup_method(s, func):
        super().setup_method(func)
        req.profile_create(s.app, s.profile)

    def test_book_create(s):
        response = s.run(req.book_create, s.app, s.profile, s.book,
                                   s.hotkey, s.active_profile)
        assert 'book created' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(s.app.db, 'Books')[0]
        assert data[0] == s.book
        assert data[1] == s.profile

        response = s.run(req.book_create, s.app, s.profile, s.book,
                                   s.hotkey, s.active_profile)
        assert 'book already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        book2 = 'asdf'
        response = s.run(req.book_create, s.app, s.profile, book2,
                                   s.hotkey, s.active_profile)
        assert 'hotkey already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = s.run(req.book_create, s.app, s.profile, book2,
                                   '', s.active_profile)
        assert 'hotkey is required' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        # Hit the code path where hokteys would get reloaded, they don't as
        # old == new, it's a state based operation, not testing for it atm
        hotkey2 = ['f7']
        s.run(req.profile_create, s.app, s.profile)
        s.run(req.profile_set_active, s.app, s.profile)
        response = s.run(req.book_create, s.app, s.profile, book2,
                                   hotkey2, s.profile)



    def test_book_delete(s):
        response = s.run(req.book_delete, s.app, 'bad_book', s.profile)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = s.run(req.book_create, s.app, s.profile, s.book,
                                   s.hotkey, s.active_profile)

        response = s.run(req.book_delete, s.app, s.book, s.profile)
        assert 'book deleted' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(s.app.db, 'Books')
        assert not data

        response = s.run(req.book_delete, s.app, s.book, s.profile)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1


class TestPage(MixInTestHelper):
    page = 'testpage'

    def test_page_create(s):
        response = s.run(req.page_create, s.app, s.profile, s.book,
                                   s.program, s.specific)
        assert 'page created' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        assert response['page_id'] == 1

        response = s.run(req.page_create, s.app, s.profile, s.book,
                                   s.program, s.specific)
        assert 'page already' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1
        assert response['page_id'] == 1


    def test_page_delete(s):
        response = s.run(req.page_delete, s.app, s.profile, s.book,
                                    'bad_page', s.specific, s.loose)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = s.run(req.page_create, s.app, s.profile, s.book,
                                   s.program, s.specific)


        data = get_all_data(s.app.db, 'Pages')
        response = s.run(req.page_delete, s.app, s.profile, s.book,
                                    s.program, s.specific, s.loose)
        assert 'page deleted' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(s.app.db, 'Pages')
        assert not data

        response = s.run(req.page_delete, s.app, s.profile, s.book,
                                    s.program, s.specific, s.loose)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

    def test_page_update(s):
        response = s.run(req.page_update, s.app, s.profile, s.book,
                                    'bad_page', s.specific, s.loose)
        assert 'does not exist' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] != 1

        response = s.run(req.page_create, s.app, s.profile, s.book,
                                   s.program, s.specific)
        data = get_all_data(s.app.db, 'Pages')

        response = s.run(req.page_update, s.app, s.profile, s.book,
                                   s.program, s.specific)
        assert 'page saved' in response['output_kwargs']['msg'].lower()
        assert response['output_kwargs']['code'] == 1
        data = get_all_data(s.app.db, 'Pages')[0]
        assert data[1] == s.profile
        assert data[2] == s.book
        assert data[3] == s.program


class TestHotkeys(MixInTestHelper):

    def test_hotkey_create(s):
        response = s.run(req.hotkey_create, s.app, s.profile, s.book,
                                     s.hotkey)
        assert 'hotkey_created' == response['output_method']

        response = s.run(req.hotkey_create, s.app, s.profile, s.book,
                                     s.hotkey)
        assert 'hotkey_taken' in response['output_method']


    def test_hotkey_delete(s):
        response = s.run(req.hotkey_delete, s.app, s.profile, s.book,
                                     s.hotkey)
        assert 'hotkey_not_found' in response['output_method']

        response = s.run(req.hotkey_create, s.app, s.profile, s.book,
                                     s.hotkey)

        response = s.run(req.hotkey_delete, s.app, s.profile, s.book,
                                     s.hotkey)
        assert 'hotkey_deleted' in response['output_method']


    def test_hotkey_updated(s):
        response = s.run(req.hotkey_update, s.app, s.profile, s.book,
                                     s.hotkey)
        assert 'hotkey_not_found' in response['output_method']

        response = s.run(req.hotkey_create, s.app, s.profile, s.book,
                                     s.hotkey)

        response = s.run(req.hotkey_update, s.app, s.profile, s.book,
                                     s.hotkey)
        assert 'hotkey_updated' in response['output_method']
        hotkey2 = ['f11']
        response = s.run(req.hotkey_update, s.app, s.profile, s.book,
                                     hotkey2)
        assert 'hotkey_not_found' in response['output_method']


    def test_hotkey_load(s):
        response = s.run(req.hotkeys_load, s.app, s.profile)
        assert not response
        dbapi.profile_create(s.app.db, s.profile)
        response = s.run(req.hotkeys_load, s.app, s.profile)
        assert not response

        dbapi.hotkey_create(s.app.db, s.profile, s.book, s.hotkey)
        hotkey2 = ['f11']
        dbapi.hotkey_create(s.app.db, s.profile, s.book, hotkey2)
        response = s.run(req.hotkeys_load, s.app, s.profile)

        assert response[0]['output_method'] == 'system_hotkey_register'
        assert response[0]['output_kwargs']['hotkey'] in (s.hotkey, hotkey2)
        assert response[1]['output_method'] == 'system_hotkey_register'
        assert response[1]['output_kwargs']['hotkey'] in (s.hotkey, hotkey2)


    def test_hotkeys_reload(s):
        response = s.run(req.hotkeys_reload, s.app, 'default', s.profile)
        assert not response

        dbapi.profile_create(s.app.db, s.profile)
        dbapi.hotkey_create(s.app.db, 'default', s.book, s.hotkey)
        dbapi.hotkey_create(s.app.db, s.profile, s.book, s.hotkey)
        response = s.run(req.hotkeys_reload, s.app, 'default', s.profile)
        assert response[0]['output_method'] == 'system_hotkey_unregister'
        assert response[1]['output_method'] == 'system_hotkey_register'


class TestUiInit(MixInTestHelper):
    def setup_class(cls):
        super().setup_class(cls)
        # move some files in that are required..
        path = os.path.abspath('deploy')
        for file in KEYMAP_FILES:
            shutil.copyfile(os.path.join(path, file),
                            os.path.join(cls.app.data_dir, file))

    def test_first_run(s):
        s.first_run = True
        response = s.run(req.first_run_init, s.app)
        assert 'window_show' == response[0]['output_method']
        assert 'welcome_screen' == response[1]['output_method']
        assert 'book_create' == response[2]['input_method']
        assert 'page_create' == response[3]['input_method']
        assert 'book_create' == response[4]['input_method']
        assert 'page_load' == response[5]['output_method']

    def test_first_run_with_profile_active(s):
        s.first_run = True
        dbapi.profile_create(s.app.db, s.profile)
        dbapi.hotkey_create(s.app.db, 'default', s.book, s.hotkey)
        dbapi.hotkey_create(s.app.db, s.profile, s.book, s.hotkey)
        response = s.run(req.ui_init, s.app, s.first_run)
        assert response[7]['output_method'] == 'system_hotkey_register'
        assert response[8]['output_method'] == 'system_hotkey_register'

    def test_all_other_runs(s):
        s.first_run = False
        response = s.run(req.ui_init, s.app, s.first_run)[0]
        assert 'profile_set_active' == response['output_method']

    def test_all_other_runs_with_profile_active(s):
        s.first_run = False
        dbapi.profile_create(s.app.db, s.profile)
        dbapi.hotkey_create(s.app.db, 'default', s.book, s.hotkey)
        dbapi.hotkey_create(s.app.db, s.profile, s.book, s.hotkey)
        response = s.run(req.ui_init, s.app, s.first_run)
        assert response[1]['output_method'] == 'system_hotkey_register'


#TODO move to own file
class TestPageFind(MixInTestHelper):
    specific = 'banking.com/page'
    program = 'testprogram'
    '''
    def test_can_find_a_specific_page(s):
        dbapi.profile_create(s.app.db, s.profile)
        dbapi.page_create(s.app.db, s.profile, s.book, s.program, None, None)
        dbapi.page_create(s.app.db, s.profile, s.book, s.program, s.specific, None)
        # resp = s.run(req.page_find, s.app.db, s.profile, s.book, s.program)
        data = get_all_data(s.app.db, 'Pages')[0]
        assert resp[4] == s.specific

    '''
    def test_page_find_general(s):
        dbapi.profile_create(s.app.db, s.profile)
        assert dbapi.page_create(s.app.db, s.profile, s.book, s.program, None, None)
        assert dbapi.page_create(s.app.db, s.profile, s.profile, s.program, 'some specifc', None)
        bookopts = {'no_process': 'write'}
        resp = s.run(req.page_find, s.app.db, s.profile, s.book, s.program, bookopts)
        assert resp
        rowid = resp
        data = get_all_data(s.app.db, 'Pages')[0]
        assert data[1] == s.profile
        assert data[2] == s.book
        assert data[3] == s.program
        assert data[4] == dbapi.UNIQUE_NULL

# Subfunc of TestHotkeyPressed
class TestNoProcess(MixInTestHelper):
    def test_basic(s):
        kwargs = {'no_process': 'shelve'}
        dbapi.book_create(s.app.db, s.profile, s.book, s.hotkey, **kwargs)
        resp = s.run(req.no_process, s.app, s.profile, s.book, s.program, s.hotkey, kwargs)
        assert resp is False

    def test_general(s):
        kwargs = {'no_process': 'write'}
        dbapi.book_create(s.app.db, s.profile, s.book, s.hotkey, **kwargs)
        resp = s.run(req.no_process, s.app, s.profile, s.book, s.program,
                     s.hotkey, kwargs)
        assert resp['page_id'] == 1
        assert resp['resp_id'] == 'page_create'
        assert resp['output_kwargs']['code'] == 1
        resp = s.run(req.no_process, s.app, s.profile, s.book, s.program,
                     s.hotkey, kwargs)
        assert resp['page_id'] == 1
        assert resp['resp_id'] == 'page_create'
        assert resp['output_kwargs']['code'] == 0
        resp = s.run(req.no_process, s.app, s.profile, s.book, s.program,
                     s.hotkey, kwargs)
        assert resp['page_id'] == 1
        assert resp['resp_id'] == 'page_create'
        assert resp['output_kwargs']['code'] == 0
        resp = s.run(req.no_process, s.app, s.profile, s.book, s.program,
                     s.hotkey, kwargs)
        assert resp['page_id'] == 1
        assert resp['resp_id'] == 'page_create'
        assert resp['output_kwargs']['code'] == 0


    # Not sure how/what i want to do, also what about a settings file???? argh
    def test_settings_inheritance(s):
        pass

    def test_settings_composition(s):
        pass

class TestHotkeyPressed(MixInTestHelper):
    def test_general_page(s):
        # Test a note gets created if need be
        dbapi.profile_create(s.app.db, s.profile)
        kwargs = {'no_process': 'write'}
        dbapi.book_create(s.app.db, s.profile, s.book, s.hotkey, **kwargs)
        program, pid, = peasoup.process_exists()

        # just a dummy valie
        system = {}

        # Test it creates and opens
        resp = s.run(req.hotkey_pressed, s.app, s.profile, program, s.hotkey,
                     system)
        assert resp[0]['resp_id'] == 'page_create'
        assert resp[0]['page_id'] == 1
        assert resp[1]['resp_id'] == 'page_load'
        assert resp[2]['resp_id'] == 'window_show'

        # just a dummy value
        system = {1: {'is_open': True}}
        # Now test we can close it on the next key press
        resp = s.run(req.hotkey_pressed, s.app, s.profile, program, s.hotkey,
                     system)
        assert resp[0]['resp_id'] == 'page_close'
        assert resp[1]['resp_id'] == 'window_hide'

        #test reopen
        system = {1: {'is_open': False}}
        resp = s.run(req.hotkey_pressed, s.app, s.profile, program, s.hotkey,
                     system)
        assert resp[0]['resp_id'] == 'page_load'
        assert resp[0]['output_kwargs']['page_id'] == 1
        assert resp[1]['resp_id'] == 'window_show'

    def test_uncrumpled_active(s):
        # If some page is open, and a page with program='uncrumpled' exists
        # only send the page_load signal
        dbapi.profile_create(s.app.db, s.profile)
        kwargs = {'no_process': 'write'}

        dbapi.book_create(s.app.db, s.profile, s.book, s.hotkey, **kwargs)
        resp = s.run(req.page_create, s.app, s.profile, s.book, s.program)
        id_1 = resp['page_id']

        system = {id_1: {'is_open': True}}
        resp = s.run(req.hotkey_pressed, s.app, s.profile, UNCRUMPLED, s.hotkey,
                     system)
        assert resp[1]['resp_id'] == 'page_create'
        id_2 = resp[1]['page_id']
        assert id_1 != id_2
        assert resp[2]['resp_id'] == 'page_load'

    def test_read_create_with_random_name(s):
        # First should create a new page
        dbapi.profile_create(s.app.db, s.profile)
        kwargs = {'no_process': 'read', 'no_read_file': 'create_with_random_name'}
        dbapi.book_create(s.app.db, s.profile, s.book, s.hotkey, **kwargs)

        system = {}
        resp = s.run(req.hotkey_pressed, s.app, s.profile, s.program, s.hotkey,
                     system)[0]
        id_1 = resp['page_id']
        assert resp['resp_id'] == 'page_create'
        assert resp['output_kwargs']['code'] == 1

        # Next calls should open the page (not create more)
        system = {id_1: {'is_open': False}}
        resp = s.run(req.hotkey_pressed, s.app, s.profile, s.program, s.hotkey,
                     system)
        assert id_1 == resp[0]['output_kwargs']['page_id']
        assert resp[0]['resp_id'] == 'page_load'


@pytest.mark.z
class TestConfigReading(MixInTestHelper):
    def setup_method(s, func):
        super().setup_method(func)
        s.app = EasyUncrumpled()

    def test_keymap_parser(s):
        keymap = """
                 window_hide: escape
                 window_show: f7 event_type=on_key_down
                 """
        # create some dummy keymaps
        for file in KEYMAP_FILES:
            with open(os.path.join(s.app.data_dir, file), 'w') as f:
                f.write(keymap)
        resp = s.run(req.parse_keymap, s.app)
        assert resp[0]['output_kwargs']['hotkey'] == ['escape']
        assert resp[0]['output_kwargs']['command'] == 'window_hide'
        assert resp[1]['output_kwargs']['hotkey'] == ['f7']
        assert resp[1]['output_kwargs']['command'] == 'window_show'
        assert resp[1]['output_kwargs']['event_type'] == 'on_key_down'

    def test_multiple_hotkey(s):
        keymap = """
                 window_hide: control f7
                 window_show: control f7 event_type=on_key_down
                 """
        for file in KEYMAP_FILES:
            with open(os.path.join(s.app.data_dir, file), 'w') as f:
                f.write(keymap)
        resp = s.run(req.parse_keymap, s.app)
        assert resp[0]['output_kwargs']['hotkey'] == ['control', 'f7']
        assert resp[0]['output_kwargs']['command'] == 'window_hide'
        assert resp[1]['output_kwargs']['hotkey'] == ['control', 'f7']
        assert resp[1]['output_kwargs']['command'] == 'window_show'
        assert resp[1]['output_kwargs']['event_type'] == 'on_key_down'

    def test_comment(s):
        keymap = """
                 window_hide: control f7
                 window_show: control f6
                 # window_show: control f7 event_type=on_key_down
                 """
        for file in KEYMAP_FILES:
            with open(os.path.join(s.app.data_dir, file), 'w') as f:
                f.write(keymap)
        resp = s.run(req.parse_keymap, s.app)
        assert len(resp) == 2


class TestCmdPane(MixInTestHelper):
    '''
    the passing of these tests required that search data be present..
    '''
    def test_search(s):
        resp = s.run(req.cmdpane_search, s.app, 'work')
        heading = resp['output_kwargs']['headings'][0]
        assert heading
        resp = s.run(req.cmdpane_item_open, s.app, heading)
        assert resp

        # test opening items
        resp = s.run(req.cmdpane_item_open, s.app, heading)
        assert resp['output_method'] == 'cmdpane_ui_build'

        # test a bad search doesn't crash us
        resp = s.run(req.cmdpane_search, s.app, '000')
        heading = resp['output_kwargs']['headings']
        assert not heading

