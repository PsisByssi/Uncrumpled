from uncrumpled.core import dbapi
from uncrumpled.core.core import core_request
from uncrumpled.core import responses as resp
from uncrumpled.core import requests as req

init_text = '''
        Uncrumpled
        ----------

        Welcome to the latest version of Uncrumpled.

        Getting Started
        ---------------
        This is your very first note page. Any time you press <Alt> + <F1>
        while the uncrumpled window is focused you will presented with this page.

        You should customize it and make it your own, jot down new things
        you have learned about uncrumpled, and have them at easy access.

        <Alt> + <F1>, is not only used for viewing this Note. We have gone
        ahead and set you up with two default notebooks. The <Alt> + <F1>
        workbook will from here on be called the learning workbook. It
        has it's "no process" settings set to "write". This Learning workbook
        will create a new note page for every program that it encounters.

        I encourage you know to Navigate to another program such as Firefox
        or Internet Explorer, and press alt F1. Remeber all you need to do
        to come back to this tutorial, is press the same key combination
        while this uncrumpled program is focused.

        Welcome Back!, I hope you had fun.
        The second workbook (named the scratchpad), can be opened with <F2>.
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
        '''

@core_request
def ui_init(core, first_run, user_or_token=None, password=None):
    '''
    Code for startup
    '''
    if first_run:
        yield resp.resp('show_window')
        yield resp.resp('welcome_screen')

        for aresp in resp.noopify(req.book_create(core, profile='default',
                             book='learning', hotkey=['alt', 'f1'],
                             active_profile='default', no_process='write')):

            yield aresp

        for aresp in resp.noopify(req.page_create(core, profile='default',
                              book='learning', program='uncrumpled',
                              init_text=init_text)):
            yield aresp

        for aresp in resp.noopify(req.book_create(core, profile='default',
                              book='scratchpad', hotkey=['f2'],
                              active_profile='default', no_process='read')):
            yield aresp

    # if data.get('new_user'):
        # yield config.new_user(data)
    # yield config.ui_config()
    profile = dbapi.profile_get_active(core.db)
    yield resp.resp('profile_set_active', profile=profile)

    for aresp in req.hotkeys_load(core, profile):
        yield aresp
