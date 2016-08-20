
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
