
import os
import asyncio

from uncrumpled.core import responses
from uncrumpled.core import requests
from uncrumpled.core import dbapi


class Core():
    def __init__(self, db):
        self.db = db
        self.messages = asyncio.Queue()
        # self.active_profile = requests.profile_get_active(self)

    # @asyncio.coroutine #ASYNC
    def request(self, data):
        '''
        call this to send data to the core
        '''
        return self.handle_request(data) # ASYNC
        # yield from self.messages.put(data)
        # response = yield from self.get_response()
        # return response

    @asyncio.coroutine
    def get_response(self):
        data = yield from self.messages.get()
        response = self.handle_request(data)
        return response

    def handle_request(self, data):
        method = data['input_method']
        kwargs = data['input_kwargs']
        if method not in responses.CORE_API:
            raise Exception('Function not supported by core, add to CORE_API')
        else:
            output_response = eval('requests.'+method+'(self, **kwargs)')
            return dict(output_response, **data) # TODO this should never override
