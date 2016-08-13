
CORE_API = ('profile_create', 'profile_delete')

_msg = {'missing_param': 'Missing parameter: {profile}',
        'profile_taken': 'Profile already in use: {profile}',
        'profile_created': 'Profile created: {profile} ',
        'profile_deleted': 'Profile deleted: {profile}',
        'profile_not_found': 'Profile does not exist: {profile}',
        'profile_changed': 'Profile changed: {profile}',
        }

def status(key, code, template):
    '''
    update the status bar
    :code: 0 or 1 for fail or success
    '''
    msg = _msg.get(key)
    assert msg != None, 'add the message to _msg dict: ' + key
    msg = msg.format(**template)
    to_send = dict({'output_method': 'status_update',
                    'output_kwargs': {'msg': msg, 'code': code},
                    })
    return to_send


_noop = ('profile_gotten',
        )

# no operation
def noop(key, **data):
    assert key in _noop, 'Add the key to noop ' + key
    return dict({'output_method': 'noop', 'key': key}, **data)

# programmer error
def prog_err(msg, **data):
    return dict({'output_method': 'programmer_error',
                'msg': msg})


_UI = ('show_window', 'welcome_screen')

def resp(method, **kwargs):
    assert method in _UI, 'Add method to_ui: ' +method
    # assert method in CORE_API, 'Add method to _ui: ' + method
    return {'output_method': method, 'output_kwargs': kwargs}
