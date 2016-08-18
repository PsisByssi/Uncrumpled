
_msg = {'book_taken': 'Book already used for this configuration',
        'book_created': 'Book created: {book}',
        'book_deleted': 'Book deleted: {book}',
        'book_not_found': 'Book does not exist: {book}',
        'hotkey_taken': 'Hotkey already used for this configuration',
        'hotkey_missing': 'A hotkey is required',
        'page_taken': 'Page already in use!',
        'page_created': 'Page created!',
        'page_updated': 'Page saved!',
        'page_not_found': 'Page does not exist!',
        'page_deleted': 'Page deleted!',
        'page_not_found': 'Page does not exist!',
        'profile_taken': 'Profile already in use: {profile}',
        'profile_created': 'Profile created: {profile} ',
        'profile_deleted': 'Profile deleted: {profile}',
        'profile_not_found': 'Profile does not exist: {profile}',
        'profile_changed': 'Profile changed: {profile}',
        }

def status(key, code, template=None):
    '''
    update the status bar
    :code: 0 or 1 for fail or success
    '''
    msg = _msg.get(key)
    assert msg != None, 'add the message to _msg dict: ' + key

    if template:
        msg = msg.format(**template)

    to_send = dict({'output_method': 'status_update',
                    'output_kwargs': {'msg': msg, 'code': code},
                    })
    return to_send


_noop = ('profile_gotten',
         'hotkey_created',
         'hotkey_taken',
         'hotkey_deleted',
         'hotkey_not_found',
         'hotkey_updated',
         'system_hotkey_register',
         'system_hotkey_unregister',
         'profile_set_active',
        )

# no operation on the ui, system operations are allowed
def noop(key, **data):
    assert key in _noop, 'Add the key to noop ' + key
    return dict(data, **{'output_method': 'noop', 'key': key, })


_UI = ('show_window', 'welcome_screen')

def resp(method, **kwargs):
    assert method in _UI, 'Add method to_ui: ' +method
    return {'output_method': method, 'output_kwargs': kwargs}
