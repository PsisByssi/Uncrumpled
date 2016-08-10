
'''
    handle communication with the gui

    the gui hands us data, we modify and send it to uncrumpled.
    The data returned is modified and added to ours system.
    System is a dict containg all the configuration options.

    This system dict layer is mainly a way to provide
    introspection to users and to work with data.
    avoid stateful functions, make testing and reason better.
    a decoupling of the core_api and the gui_api.
    Thesecould be called 1-1  but anyway.

    we can change this dict and call update_cfg
    to update anything on the gui side.

    the gui must support the following methods

    feature_check:
        if the function is safe to run return true
'''

from kivygui import KivyGui

SYSTEM = {'binds': {},
          'bind_handlers': []}

gui = KivyGui()
# system hk format
# binds = {event_type: {hk [cb1, cb2]}]

def start(app=None):
    # global gui
    test_update={'add_bind': {'hotkey':'f5',
                        'event_type':'key_down',
                        'command':'toggle'}}
    update_cfg(gui, test_update, SYSTEM)
    # apply_cfg(SYSTEM)
    gui.run()

# input format
# {'add_bind': {'hotkey': '', 'event_type': '', 'command'}}
# {'add_bind'}

# TODO until i can get apply_cfg to work just doing it here
def update_cfg(gui, update: dict, system:dict):
    '''
    takes a update to the system dict from the uncrumpled core
    adds it the the system config in proper format
    '''
    for action, kwds in update.items():
        if action == 'add_bind':
            try:
                add_bind(gui,
                         kwds['event_type'],
                         kwds['hotkey'],
                         kwds['command'],
                         system)
                eval('gui.root.bind({}={}'.format(
                                        kwds['event_type'],
                                        kwds['command']))
            except Exception:
                raise Exception # TODO
        # elif action == 'attribute':
            # gui.do_attribute(value)

"""
def apply_cfg(gui, updated:dict):
    '''
    iterate over the sytem and apply the changes to our
    gui
    '''
    diffed == DictDiffer(updated, system):
    for key in diffed.added():
        if key == 'binds':
            bind_cfg = DictDiffer(updated['binds']).added()
"""
COMMANDS = {'toggle':gui.toggle}
BINDS = []
CALLBACKS = []

#UI SPECIFIC
def key_down_handler(_, __, keycode, keysym, modifiers, system):
    '''
    checks if the key has a callback bound to it and
    runs it
    '''
    get_hkstring(keysym, modifiers)
    callbacks =  system['binds']['key_down'].get(hkstring)
    for cb in callbacks:
        if cb not in BINDS:
            cb()

# Avaliable event handlers the gui supports
EVENT_HANDLERS = {'key_down':key_down_handler}


def add_bind(gui, event_type:str, hk:str, command:list,
                                            system:dict):
    '''
    add a bind to the system
    '''
    for cb in command:
        if cb not in COMMANDS:
            raise Exception('Bad Callback in add_bind: ', cb)

    if not system['bind_handlers'].get(event_type):
        init_bind_handler(event_type)
    init_bind(hk, event_type, command)


def remove_bind(gui, event_type:str, hk:str, command:dict,
                                                system:dict):
    for i, func in enumerate(system['binds'][event_type][hk]):
        if func == command:
            del system['binds']['event_type']['hk'][i]
            break


def init_bind_handler(event_type:str, system:dict) -> None:
    '''
    Setup a function to handle a certain type of event.
    All events of that type get filtered through this function.

    so for key_down event, a function will be initalized to grab
    all those keys.
    '''
    handler = EVENT_HANDLERS.get(event_type)
    if function:
        system['binds']['active_handlers'] = handler
    else:
        raise Exception('invalid event type')

def init_bind(hk, event_type, command, system):
    commands = system['binds'][event_type][hk].setdefault([])
    commands.append(command)

