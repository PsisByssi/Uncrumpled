'''
    Uncrumpled Presenter

    handle communication with the gui

    the gui calls us directly.

    the return data from the core is modified and added to our system.
    system is a dict containg all the configuration options used
    by the gui.
'''

import asyncio
from functools import wraps
from types import GeneratorType
from collections import Iterable

from uncrumpled.presenter import responses
from timstools import make_class_name


def uncrumpled_request(func):
    '''
    all api exposed functions are wrapped here

    :return:
        a list of strings(functions) that the frontend should run
    '''
    # @asyncio.coroutine #ASYNC
    def wrapper(app, *args, **kwargs):
        # core_response = yield from func(app, *args, **kwargs)# ASYNC
        core_responses = func(app, *args, **kwargs)
        result = []
        try:
            for resp in core_responses:
                resp_handler = update_system(app, resp)
                if not resp_handler:
                    raise Exception('Create handler for ' + resp['resp_id'])
                _res = resp_handler.partial_ui_update()
                if _res:
                    result.append(_res)
            return result
        except Exception as err:
            # TODO Seems kivy has an issue raising errors from
            # generators...
            print('Core response had an error...')
            import pdb;pdb.set_trace()
            # WOW without this the err var is unbound...
            raise err
    return wrapper


def update_system(app, response):
    '''
    takes a update to the system dict from the uncrumpled core
    adds it the the system config in proper format
    '''
    try:
        cls = make_class_name(response['resp_id'])
    except KeyError:
        import pdb;pdb.set_trace()
    except TypeError:
        import pdb;pdb.set_trace()
    try:
        response_handler = eval('responses.{}(app.SYSTEM, response, app)'
                            .format(cls))
    except AttributeError:
        pass
    else:
        response_handler.add_to_system()
        return response_handler
