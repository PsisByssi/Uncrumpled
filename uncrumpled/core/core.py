
import asyncio
from functools import wraps

# from uncrumpled.core import responses
# from uncrumpled.core import requests
# from uncrumpled.core import dbapi


def core_request(is_resp_id=False):
    def wrapper(func):
        def _core_request(*args, **kwargs):
            data = {}
            if is_resp_id:
                data['resp_id'] = func.__name__
            response = func(*args, **kwargs)
            for aresp in response:
                # A toplevel request
                if not aresp.get('input_method'):
                    data['input_method'] = func.__name__
                    data['input_kwargs'] = kwargs
                    yield dict(aresp, **data)
                else:
                    yield aresp
        return _core_request
    return wrapper

#################### DEL
class Core():
    def __init__(self, db):
        self.db = db
        self.messages = asyncio.Queue()
        # self.active_profile = requests.profile_get_active(self)

    # @asyncio.coroutine #ASYNC
    def request(self, data, *args):
        '''
        call this to send data to the core

        :data: the input request modified to our pleasure
        :args: provided by the presenter, normally some system state

        :return: [{output1}, {output2}]
        '''
        return list(self.handle_request(data, args)) # ASYNC
        # yield from self.messages.put(data)
        # response = yield from self.get_response()
        # return response

    @asyncio.coroutine
    def get_response(self):
        data = yield from self.messages.get()
        response = self.handle_request(data)
        return response

    def handle_request(self, data, args):
        method = data['input_method']
        kwargs = data['input_kwargs']
        abc = args
        if method not in requests.CORE_API:
            raise Exception('Function not supported by core, add to CORE_API '+ method)
        else:
            output_response = eval('requests.'+method+'(self, *args, **kwargs)')
            for aresp in output_response:
                yield dict(aresp, **data) # TODO this should never override
