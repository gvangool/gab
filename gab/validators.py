def validate_not_empty(value, key='value'):
    'Validate whether an actual value was typed'
    if value.strip() == '':
        raise Exception('Please provide a %s.' % key)
    return value


def yes_or_no(value):
    'Validate whether a user types yes (y) or no (n)'
    value = value.strip().lower()
    if len(value) == 0 or value[0] not in ('y', 'n',):
        raise Exception('Please type [y]es or [n]o.')
    return value
