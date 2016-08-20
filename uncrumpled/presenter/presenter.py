'''
    Uncrumpled Presenter

    handle communication with the gui

    the gui calls us directly.

    the return data from the core is modified and added to our system.
    system is a dict containg all the configuration options used
    by the gui.

    If we use rpc for the api parts of this will remain here
    specifically the bits related with updating the system
    The gui will need it's own presenter to communicate with us though.
'''

import asyncio
from functools import wraps
from types import GeneratorType
from collections import Iterable

from uncrumpled.presenter import responses
from uncrumpled.presenter import util

SYSTEM = dict(util.system_base)


def uncrumpled_request(func):
    '''
    all api exposed functions are wrapped here

    :return:
        a list of strings to be evaled
    '''
    # @asyncio.coroutine #ASYNC
    def wrapper(app, *args, **kwargs):
        # core_response = yield from func(app.core, *args, **kwargs)# ASYNC
        core_responses = func(app, *args, **kwargs)
        result = []
        for resp in core_responses:
            resp_handler = update_system(resp)
            _res =resp_handler.partial_ui_update()
            if _res:
                result.append(_res)
        return result
    return wrapper


def update_system(response):
    '''
    takes a update to the system dict from the uncrumpled core
    adds it the the system config in proper format
    '''
    class_name = util.make_class_name(response['input_method'])
    response_handler = eval('responses.{}(SYSTEM, response)'.format(class_name))
    response_handler.add_to_system()
    return response_handler
