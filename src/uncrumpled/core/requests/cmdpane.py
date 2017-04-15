
from piefuzz import Fzf
from timstools import Singleton

from uncrumpled.core import requests as req
from uncrumpled.core import responses as resp
from uncrumpled.core.core import core_request


GROUPS = ('settings',
          'workbook')

fzf = Fzf(fzf_path=None)

class SourceItem():
    '''
    a search item
    '''
    def __init__(self, group, body=None, ui=None, func=None):
        assert group in GROUPS
        self.ui=ui
        self.body=body
        self.func=func

# the ideal solution would be to
# write the items as help files
# or parse existing python documentation
# but i don't like text parsing hahaha!
class Source(metaclass=Singleton):
    '''
    All the stuff our cmdpane searchs through
    '''
    def __init__(self):
        self.data = {}
        self.gen_source()

    # TODO write to disk instead of holding this in memory
    def add(self, heading, group, body=None, ui=None, func=None):
        source = '{}: {}'.format(group, heading)
        self.data[source] = SourceItem(group, body, ui, func)

    def gen_source(s): # TODO plugin system so i don't have to keep messing with the front end when i add items here
        s.add('Create Workbook', group='workbook', ui='workbook_create')
        s.add('Create TEST', group='workbook', ui='workbook_create')
        s.add('Create TEST MORE', group='workbook', ui='workbook_create')

    def get(self):
        return (k for k in self.data.keys())

    def parse_results(self, fuzzed):
        '''
        fuzzed: data that has been fuzzed
        output -> two lists, (headings, bodies)
        '''
        bodies = [self.data[x].body for x in fuzzed]
        return fuzzed, bodies


@core_request()
def cmdpane_search(app, query: str):
    input = Source().get()
    fuzzed = fzf.fuzz(query, input_list=input).splitlines()
    heads, bodies = Source().parse_results(fuzzed)
    yield resp.resp('cmdpane_search_results', headings=heads,
                                              bodies=bodies)

@core_request(is_resp_id=True)
def cmdpane_item_open(app, item):
    '''
    the user has pressed enter on a result..
    '''
    result = Source().data[item]
    if result.ui:
        yield resp.resp('cmdpane_ui_build', ui=result.ui)
    else:
        import pdb;pdb.set_trace()
