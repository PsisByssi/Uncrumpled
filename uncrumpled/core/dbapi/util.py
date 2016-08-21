
# A unique constraint is satisfied if and only if no two rows in a table have the same values and have non-null values in the unique columns.
# This is required to make the unique constraint blow i.e values must
# not be null for the unique constarint to work.
UNIQUE_NULL = ">X~"

import halt

def page_validate(profile, book, program, specific, loose):
    '''
    see _page_save, incase any None values float in.
    transform them to our null value representation.

    '''
    if not program: program = UNIQUE_NULL
    if not specific: specific = UNIQUE_NULL
    if not loose: loose = UNIQUE_NULL
    return (profile, book, program, specific, loose)


def page_rowid_get(db, profile, book, program, specific, loose):
    page = page_validate(profile, book, program, specific, loose)
    cond = "WHERE Profile == '{}' AND \
                  Book == '{}' AND \
                  Program == '{}' AND \
                  Specific == '{}' AND \
                  Loose == '{}'".format(*page)
    rowid = halt.load_column(db, 'Pages', ('Id',), cond=cond)
    if not rowid:
        return False
    else:
        return rowid[0][0]


def page_info(db, page_id, rv=list): # TODO delete?
    '''given a page_id, get all page info in as a tuple or dictionary'''
    assert rv in (list, dict)
    cond = "WHERE Id == '{}'".format(page_id)
    result = halt.load_column(db, 'Pages', ('*',), cond)
    import pdb;pdb.set_trace()
    if rv == tuple:
        return result
    else:
        obj = {'Id': page_id, 'Profile': result[1], 'Book': result[2],
               'Program': result[3], 'Specific': result[4],
               'Loose':result[5], 'UFile': result[6], 'MashConfig': result[7]}
        return obj
