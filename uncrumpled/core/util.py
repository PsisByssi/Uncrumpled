'''
    Random helper utilites
'''

import os
import random
import string

import halt

from uncrumpled.core import dbapi

def _create_name(page_id):
    '''
    :return: symlink name, just the page_id with extension:)
    '''
    return '{}.lnk'.format(page_id)


def rand_str(length):
    '''returns a random string of length'''
    chars = []
    for i in range(length):
        chars.append(random.choice(string.ascii_letters))
    return ''.join(char for char in chars)


def _rand_name_in_dir(dir):
    '''returns a str not found in a dir'''
    fname = rand_str(8)
    while fname in os.listdir(dir):
        fname = rand_str(8)
    return fname


def ufile_get(db, page_id):
    cond = "WHERE Id == '{}'".format(page_id)
    ufile = halt.load_column(db, 'Pages', ('Ufile',), cond)
    ufile = halt.load_column(db, 'Pages', ('Ufile',), cond)[0][0]
    if ufile:
        return ufile
    return False


# Generate a new file (randomly named), it's saved in the database
def ufile_create(app, page_id, init_text=None):
    fname = _rand_name_in_dir(app.notedir) + '.uncrumpled'
    dbapi.ufile_create(app.db, page_id, fname)

    # import pdb;pdb.set_trace()
    if init_text:
        with open(os.path.join(app.notedir, fname), 'w') as f:
            f.write(init_text)
    return fname
