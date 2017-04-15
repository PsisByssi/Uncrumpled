
import os

import yaml
from yamlordereddictloader import Loader as OrderedLoader

from uncrumpled.core import dbapi
from uncrumpled.core import plugin
from uncrumpled.core.core import core_request
from uncrumpled.core import responses as resp
from uncrumpled.core import requests as req

key1 = '<F2>'
key2 = '<F3>'

init_text = '''
        Uncrumpled
        ----------

        Welcome to the latest version of Uncrumpled.

        Getting Started
        ---------------
        This is your very first note page. Any time you press {key1}
        while the uncrumpled window is focused you will presented with this page.

        You should customize it and make it your own, jot down new things
        you have learned about uncrumpled, and have them at easy access.

        {key1}, is not only used for viewing this Note. We have gone
        ahead and set you up with two default notebooks. The {key1}
        workbook will from here on be called the learning workbook. It
        has it's "no process" settings set to "write". This Learning workbook
        will create a new note page for every program that it encounters.

        I encourage you know to Navigate to another program such as Firefox
        or Internet Explorer, and press {key1}. Remeber all you need to do
        to come back to this tutorial, is press the same key combination
        while this uncrumpled program is focused.

        Welcome Back!, I hope you had fun.
        The second workbook (named the scratchpad), can be opened with {key2}.
        It's a little different to the learning workbook as it has it's
        "no process" setting set to "read". This means it will only create
        new notes if you tell it to. Otherwise it will open the last used
        note. It's perfect for working on working on a persitance idea
        across programs.

        Additional Resources
        --------------------

        If you are new please check out the Online `Docs`
        You can also use the `Command Pane` for quick
        help on anything in Uncrumpled `Ctrl + Space`

        If you run into any problems please report them on `Github`!
        '''.format(key1=key1, key2=key2)


KEYMAP_FILES = ('default.keymap',)

def get_contents(file):
    with open(file) as f:
        return yaml.load(f.read(), Loader=OrderedLoader)


def get_kwargs(value):
    try:
        values = value.split(' ')
    except AttributeError:
        # Integer hotkey with no arguments
        if type(value) == int:
            hotkey = value
            return [hotkey], {}
        raise
    else:
        hotkey = []
        found_kwargs = False
        for i, x in enumerate(values):
            # if still in hotkey
            if '=' in x and len(x) > 1:
                found_kwargs = True
                break
            else:
                hotkey.append(x)

        if found_kwargs:
            pairs = (x.split('=') for x in values[i:])
            kwargs = {k : v for k, v in pairs}
        else:
            kwargs = {}
        # if type(hotkey) == str:
            # hotkey = [hotkey]
        return hotkey, kwargs

'''
TODO further ideas

We want to develop this out to be quite flexible
a seperate tool woul be deveoped that uses generated data to determine
if the script is valid (static type checking) api points etc

also not just yaml files but full blown python files
use the importlib module
'''
@core_request()
def parse_keymap(app):
    '''
    reads the default keymap file, then the user keymap file

    pound #, can be used for comments
    '''
    for file in KEYMAP_FILES:
        data = get_contents(os.path.join(app.data_dir, file))
        for action, keybind in data.items():
            if action not in resp._UI:
                import pdb;pdb.set_trace()
                raise Exception('{} not in supported ui'.format(action))

            hk, kwargs = get_kwargs(keybind)
            yield resp.resp('bind_add', resp_id='bind_add',
                            hotkey=hk, event_type=kwargs.get('event_type'),
                            command=action, command_kwargs=kwargs)


def first_run_init(app):
    yield resp.resp('window_show')
    yield resp.resp('welcome_screen')

    for aresp in resp.noopify(req.book_create(app, profile='default',
                         book='learning', hotkey=['f2'],
                         active_profile='default', no_process='write')):

        yield aresp

    for aresp in resp.noopify(req.page_create(app, profile='default',
                          book='learning', program='uncrumpled',
                          init_text=init_text)):
        page_id = aresp['page_id']
        yield aresp

    for aresp in resp.noopify(req.book_create(app, profile='default',
                          book='scratchpad', hotkey=['f3'],
                          active_profile='default', no_process='read')):
        yield aresp
    yield resp.resp('page_load', page_id=page_id)


def sys_init(system):
    system['functions'] = plugin.get_functions()
    system['ui_event_types'] = plugin.get_event_types()


@core_request()
def ui_init(app, first_run, user_or_token=None, password=None):
    '''
    Code for startup
    '''
    # Setup default books etc
    if first_run:
        yield from first_run_init(app)

    # if data.get('new_user'):
        # yield config.new_user(data)
    # yield config.ui_config()

    # Setup the system
    sys_init(app.SYSTEM)

    # Set active profile
    profile = dbapi.profile_get_active(app.db)
    yield resp.resp('profile_set_active', profile=profile)

    # Load hotkeys
    for aresp in req.hotkeys_load_all(app, profile):
        yield aresp

    # Load keymap
    for aresp in parse_keymap(app):
        yield aresp

    # Load settings files
    # should start minimized/or sth etc
