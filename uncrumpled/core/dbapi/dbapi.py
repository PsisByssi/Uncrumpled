'''
    talks to sql db using halt
'''

import halt

def profile_create(db, name):
    '''
    saves a new profile entry in the database
    '''
    try:
        halt.insert(db, 'Profiles', {"name": name})
    except halt.HaltException:
        return False
    else:
        return True


def profile_delete(db, profile):
    if profile not in profile_get_all(db):
        return False
    cond = "where Name == '{0}'".format(profile)
    halt.delete(db, 'Profiles', cond)
    return True


def profile_set_active(db, profile):
    '''Sets the given profile as being active'''
    # Remove the previous active
    cond = "where Active == 1"
    halt.update(db, 'Profiles', {'Active': False}, cond)

    # Update the new
    cond = "where Name == '{0}'".format(profile)
    halt.update(db, 'Profiles', {'Active': True},  cond)


def profile_get_active(db):
    '''Returns the currently active profile'''
    cond = "where Active == 1"
    results = halt.load_column(db, 'Profiles', ('Name',) , cond)
    profile = results[0][0]
    return profile


def profile_get_all(db):
    '''
    Returns a list of profiles on the system
    '''
    results = halt.load_column(db, 'Profiles', ('Name',))
    return [x[0] for x in results]


