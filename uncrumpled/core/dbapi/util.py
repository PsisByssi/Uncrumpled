
def page_select(profile, book, program, specific, loose):
    if loose:
        return "WHERE Loose == '{}'".format(loose)

    cond = "WHERE Profile=='{}' AND Book=='{}' AND Program=='{}'"
    cond = cond.format(profile, book, program)
    if not specific:
        return cond

    return cond + " AND Specific=='{}'".format(specific)
