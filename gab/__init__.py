#: The version list
VERSION = (1, 0, 1)


def get_version():
    '''
    Converts the :attr:`VERSION` into a nice string
    '''
    if len(VERSION) > 3 and VERSION[3] != 'final' and VERSION[3] != '':
        return '%s.%s.%s %s' % (VERSION[0], VERSION[1], VERSION[2], VERSION[3])
    else:
        return '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])


#: The actual version number, used by python (and shown in sentry)
__version__ = get_version()
